from __future__ import annotations
import json, statistics, time
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.harness_core import BoundedWorkerRequest, ChangeScope, ContextItem, ContextItemKind, build_context_pack, validate_candidate
from tools.ollama_worker import call_bounded_stateless_worker

OUT=Path(__file__).with_name('result.json')
TASKS=[('single-'+str(i),f'Implement function task_{i}(value) in src/module.py. Return value + {i}.') for i in range(1,7)]+[('semantic','Implement is_valid(value): return False for None or empty string, otherwise True.'),('boundary','Implement clamp(value, low, high) with inclusive bounds.'),('exception','Implement divide(a,b), raising ValueError when b is zero.'),('parser','Implement parse_flag(text): trimmed case-insensitive yes/no to bool, otherwise ValueError.'),('multi','Implement format_status(value) in src/module.py and caller_status(value) in src/caller.py consistently.'),('coordination','Implement normalize_name(value) in src/module.py and use it from src/caller.py.')]
def run(strong):
 rows=[]; t0=time.perf_counter()
 for tid,goal in TASKS:
  pack=build_context_pack(task_id=tid,goal=goal,acceptance_criteria=('produce a correct implementation','modify only approved source paths'),allowed_changes=('src/module.py','src/caller.py'),forbidden_changes=('tests/independent.py','all other paths'),items=(ContextItem(ContextItemKind.SOURCE_FILE,'src/module.py','def placeholder(value):\n    return value\n'),ContextItem(ContextItemKind.TEST_FILE,'tests/visible.py','assert the stated function contract')),output_contract={'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True},budget_chars=20000)
  extra=' Candidate paths MUST exactly match one of the authorized paths supplied by the Harness. Do not shorten, rename, infer, normalize, or invent paths. Use the exact provenance path.' if strong else ''
  req=BoundedWorkerRequest(task=tid+'\n'+goal+extra,context_pack={'task_id':pack.task_id,'goal':pack.goal,'acceptance_criteria':pack.acceptance_criteria,'allowed_changes':pack.allowed_changes,'forbidden_changes':pack.forbidden_changes,'items':[{'kind':x.kind.value,'source':x.source,'content':x.content} for x in pack.items]},output_contract={'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True})
  r=call_bounded_stateless_worker(req); paths=[] if not r.candidate else [o.path for o in r.candidate.operations]; v=validate_candidate(r.candidate,ChangeScope(('src/module.py','src/caller.py'),('tests/independent.py',))) if r.candidate else None
  rows.append({'task_id':tid,'paths':paths,'transport':r.transport_ok,'parse':bool(r.candidate),'validator':bool(v and v.valid),'elapsed':r.metadata.get('elapsed_seconds'),'error':r.error})
 return rows,time.perf_counter()-t0
def main():
 if OUT.exists(): return
 a,ta=run(False); b,tb=run(True)
 def summarize(rows): return {'transport':sum(x['transport'] for x in rows),'parse':sum(x['parse'] for x in rows),'validator':sum(x['validator'] for x in rows),'aligned':sum(x['validator'] for x in rows),'mean':statistics.mean(x['elapsed'] for x in rows if x['elapsed'] is not None),'median':statistics.median(x['elapsed'] for x in rows if x['elapsed'] is not None)}
 OUT.write_text(json.dumps({'experiment':'VNEXT-007P','task_count':len(TASKS),'A_current':{'summary':summarize(a),'rows':a,'wall':ta},'B_path_contract':{'summary':summarize(b),'rows':b,'wall':tb},'authorized_paths':['src/module.py','src/caller.py'],'safety':{'validator_relaxed':False,'path_repaired':0,'original_mutation':0}},indent=2),encoding='utf-8')
if __name__=='__main__':main()

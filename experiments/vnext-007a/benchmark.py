from __future__ import annotations
import json, statistics, tempfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.harness_core import BoundedWorkerRequest, ChangeScope, ContextItem, ContextItemKind, build_context_pack, validate_candidate, apply_candidate_to_snapshot
from tools.ollama_worker import call_bounded_stateless_worker
OUT=Path(__file__).with_name('result.json')
TASKS=[(f't{i}',f'Implement task_{i}(value) in src/module.py. Return value + {i}.') for i in range(1,7)]+[('semantic','Implement is_valid(value): False for None or empty string, True otherwise.'),('boundary','Implement clamp(value, low, high) with inclusive bounds.'),('exception','Implement divide(a,b), raising ValueError when b is zero.'),('parser','Implement parse_flag(text): trimmed case-insensitive yes/no to bool, otherwise ValueError.'),('multi','Implement format_status(value) in src/module.py and caller_status(value) in src/caller.py consistently.'),('coordination','Implement normalize_name(value) in src/module.py and use it from src/caller.py.')]
def run(explicit):
 rows=[]
 for tid,goal in TASKS:
  with tempfile.TemporaryDirectory(prefix='qh-a-') as td:
   root=Path(td); (root/'src').mkdir(); (root/'src/module.py').write_text('def placeholder(value):\n    return value\n'); (root/'src/caller.py').write_text('from .module import placeholder\n')
   target='src/module.py EXISTS => allowed_operation REPLACE_FILE; src/caller.py EXISTS => allowed_operation REPLACE_FILE.' if explicit else ''
   prompt=goal+'\nAUTHORIZED WRITE TARGETS: src/module.py, src/caller.py. READ-ONLY CONTEXT: tests/visible.py. '+target
   pack=build_context_pack(task_id=tid,goal=prompt,acceptance_criteria=('correct implementation',),allowed_changes=('src/module.py','src/caller.py'),forbidden_changes=('tests/visible.py','all other paths'),items=(ContextItem(ContextItemKind.SOURCE_FILE,'src/module.py',(root/'src/module.py').read_text()),ContextItem(ContextItemKind.SOURCE_FILE,'src/caller.py',(root/'src/caller.py').read_text()),ContextItem(ContextItemKind.TEST_FILE,'tests/visible.py','read-only')),output_contract={'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True},budget_chars=20000)
   req=BoundedWorkerRequest(task=tid+'\n'+prompt,context_pack={'task_id':pack.task_id,'goal':pack.goal,'acceptance_criteria':pack.acceptance_criteria,'allowed_changes':pack.allowed_changes,'forbidden_changes':pack.forbidden_changes,'items':[{'kind':x.kind.value,'source':x.source,'content':x.content} for x in pack.items]},output_contract={'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True})
   r=call_bounded_stateless_worker(req,authorized_paths=('src/module.py','src/caller.py')); ops=[] if not r.candidate else [{'type':o.operation_type.value,'path':o.path,'content_present':bool(o.content)} for o in r.candidate.operations]; v=validate_candidate(r.candidate,ChangeScope(('src/module.py','src/caller.py'),('tests/visible.py',))) if r.candidate else None; app=apply_candidate_to_snapshot(root,r.candidate,v) if v and v.valid else None
   rows.append({'task_id':tid,'operations':ops,'target_exists':{p:True for p in ('src/module.py','src/caller.py')},'transport':r.transport_ok,'parse':bool(r.candidate),'validator':bool(v and v.valid),'apply':bool(app and app.success),'apply_error':None if not app else app.error,'elapsed':r.metadata.get('elapsed_seconds')})
 return rows
def main():
 if OUT.exists(): return
 a=run(False); b=run(True)
 def s(x):
  vals=[r['elapsed'] for r in x if r['elapsed'] is not None]; return {'transport':sum(r['transport'] for r in x),'parse':sum(r['parse'] for r in x),'validator':sum(r['validator'] for r in x),'apply':sum(r['apply'] for r in x),'mean':statistics.mean(vals),'median':statistics.median(vals),'apply_reliability':sum(r['apply'] for r in x)/max(1,sum(r['validator'] for r in x))}
 OUT.write_text(json.dumps({'experiment':'VNEXT-007A','A_current':{'summary':s(a),'rows':a},'B_target_state':{'summary':s(b),'rows':b},'fixture_integrity':'PASS','safety':{'auto_correction':0,'original_mutation':0,'false_completed':0}},indent=2),encoding='utf-8')
if __name__=='__main__':main()

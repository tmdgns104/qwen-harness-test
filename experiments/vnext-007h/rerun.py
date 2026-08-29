from __future__ import annotations
import json, statistics, time
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.harness_core import BoundedWorkerRequest, ChangeScope, ContextItem, ContextItemKind, build_context_pack, validate_candidate
from tools.ollama_worker import call_bounded_stateless_worker
OUT=Path(__file__).with_name('rerun_result.json')
def main():
 rows=[]
 for i,goal in enumerate(['Implement add(a,b) returning a+b.','Implement normalize_name(value) trimming and lowercasing.','Implement clamp(value, low, high) with inclusive bounds.','Implement parse_flag(text) for yes/no.','Implement format_status(value) for ready/blocked.']):
  pack=build_context_pack(task_id=f'R{i}',goal=goal,acceptance_criteria=('strict JSON Candidate',),allowed_changes=('src/module.py',),forbidden_changes=('all other paths',),items=(ContextItem(ContextItemKind.SOURCE_FILE,'src/module.py','def placeholder(value):\n    raise NotImplementedError\n'),),output_contract={'operations':['CREATE_FILE','REPLACE_FILE']},budget_chars=10000)
  req=BoundedWorkerRequest(goal,{'task_id':pack.task_id,'goal':pack.goal,'acceptance_criteria':pack.acceptance_criteria,'allowed_changes':pack.allowed_changes,'forbidden_changes':pack.forbidden_changes,'items':[{'kind':x.kind.value,'source':x.source,'content':x.content} for x in pack.items]}, {'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True})
  t=time.perf_counter(); r=call_bounded_stateless_worker(req); elapsed=time.perf_counter()-t; vr=None
  if r.candidate is not None: vr=validate_candidate(r.candidate,ChangeScope(('src/module.py',),('tests/**',)))
  rows.append({'task_id':f'R{i}','elapsed':elapsed,'transport_ok':r.transport_ok,'parse_ok':r.candidate is not None,'validator_ok':None if vr is None else vr.valid,'candidate_ops':0 if r.candidate is None else len(r.candidate.operations),'error':r.error})
 OUT.write_text(json.dumps({'rows':rows,'mean_elapsed':statistics.mean(x['elapsed'] for x in rows),'median_elapsed':statistics.median(x['elapsed'] for x in rows)},indent=2),encoding='utf-8')
if __name__=='__main__':main()

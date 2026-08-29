from __future__ import annotations
import json, statistics, subprocess, time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.harness_core import BoundedWorkerRequest, ContextItem, ContextItemKind, build_context_pack, validate_candidate
from tools.ollama_worker import call_bounded_stateless_worker

OUT=Path(__file__).with_name('result.json'); MODEL='qwen3:8b'
TASKS=[
 ('empty','Implement normalize_name(value): None/blank -> "", else trim lowercase.'),
 ('boundary','Implement clamp(value, low, high), inclusive bounds.'),
 ('exception','Implement divide(a,b), raising ValueError when b is zero.'),
 ('state','Implement toggle(value) returning the boolean opposite.'),
 ('offbyone','Implement take_prefix(items,n); n=0 gives [], negative n raises ValueError.'),
 ('parser','Implement parse_flag(text): trimmed case-insensitive yes/no to bool, otherwise ValueError.'),
 ('semantic','Implement is_even(n), including zero and negative integers.'),
 ('multifile','Implement format_status(value), ready for True and blocked otherwise.'),
 ('coordinated','Implement greeting(name) returning Hello, <name>!.'),
 ('edge','Implement safe_len(value): None -> 0, otherwise len(value).'),
]
def hardware():
 def run(args):
  p=subprocess.run(args,capture_output=True,text=True,timeout=10); return p.stdout.strip()
 return {'ollama_ps':run(['ollama','ps']),'nvidia_smi':run(['nvidia-smi','--query-gpu=memory.used,memory.total','--format=csv,noheader'])}
def main():
 if OUT.exists():
  return
 rows=[]; before=hardware()
 for tid,goal in TASKS:
  t0=time.perf_counter(); pack=build_context_pack(task_id=tid,goal=goal,acceptance_criteria=('satisfy task','modify only src/module.py'),allowed_changes=('src/module.py',),forbidden_changes=('all other paths',),items=(ContextItem(ContextItemKind.SOURCE_FILE,'src/module.py','def placeholder(value):\n    raise NotImplementedError\n'),ContextItem(ContextItemKind.TEST_FILE,'tests/test_visible.py','visible test contract supplied'),),output_contract={'operations':['CREATE_FILE','REPLACE_FILE']},budget_chars=20000); build_elapsed=time.perf_counter()-t0
  request=BoundedWorkerRequest(task=f'{tid}: {goal}',context_pack={'task_id':pack.task_id,'goal':pack.goal,'acceptance_criteria':pack.acceptance_criteria,'allowed_changes':pack.allowed_changes,'forbidden_changes':pack.forbidden_changes,'items':[{'kind':x.kind.value,'source':x.source,'content':x.content} for x in pack.items]},output_contract={'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True})
  r=call_bounded_stateless_worker(request,model=MODEL); parse_ok=r.candidate is not None; stage='TRANSPORT' if not r.transport_ok else ('CANDIDATE_PARSE' if not parse_ok else 'CANDIDATE_VALIDATION')
  validation=None
  if parse_ok:
   validation=validate_candidate(r.candidate, __import__('tools.harness_core',fromlist=['ChangeScope']).ChangeScope(('src/module.py',),('tests/**',))); stage='CANDIDATE_VALIDATION' if not validation.valid else 'SNAPSHOT_APPLY'
  rows.append({'task_id':tid,'context_chars':pack.used_chars,'request_chars':len(json.dumps(request.context_pack,ensure_ascii=False)),'context_build_seconds':build_elapsed,'inference_seconds':r.metadata.get('elapsed_seconds'),'transport_ok':r.transport_ok,'parse_ok':parse_ok,'validation':None if validation is None else {'valid':validation.valid,'errors':validation.errors},'stage_failure':None if parse_ok and validation and validation.valid else stage,'candidate':None if r.candidate is None else [{'operation_type':x.operation_type.value,'path':x.path,'content_len':len(x.content)} for x in r.candidate.operations],'error':r.error})
 after=hardware(); inf=[x['inference_seconds'] for x in rows if x['inference_seconds'] is not None]
 funnel={'total':len(rows),'transport_ok':sum(x['transport_ok'] for x in rows),'parse_ok':sum(x['parse_ok'] for x in rows),'validation_pass':sum(bool(x['validation'] and x['validation']['valid']) for x in rows),'snapshot_apply_pass':0,'visible_pass':0,'independent_pass':0,'completed':0}
 OUT.write_text(json.dumps({'experiment':'vnext-007','model':MODEL,'settings':{'think':False,'temperature':0,'seed':424242,'num_ctx':8192},'tasks':TASKS,'funnel':funnel,'latency':{'inference_mean':statistics.mean(inf) if inf else None,'inference_median':statistics.median(inf) if inf else None},'hardware_before':before,'hardware_after':after,'rows':rows},indent=2,ensure_ascii=False),encoding='utf-8')
if __name__=='__main__':main()

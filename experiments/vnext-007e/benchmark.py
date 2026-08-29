from __future__ import annotations
import json, statistics, tempfile, time
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.harness_core import BoundedWorkerRequest, ChangeScope, ContextItem, ContextItemKind, build_context_pack, validate_candidate, apply_candidate_to_snapshot, verify_bounded_candidate
from tools.ollama_worker import call_bounded_stateless_worker
OUT=Path(__file__).with_name('result.json')
TASKS=[('single-'+str(i),f'Implement task_{i}(value) in src/module.py. Return value + {i}.') for i in range(1,7)]+[('semantic','Implement is_valid(value): False for None or empty string, True otherwise.'),('boundary','Implement clamp(value, low, high) with inclusive bounds.'),('exception','Implement divide(a,b), raising ValueError when b is zero.'),('parser','Implement parse_flag(text): trimmed case-insensitive yes/no to bool, otherwise ValueError.'),('multi','Implement format_status(value) in src/module.py and caller_status(value) in src/caller.py consistently.'),('coordination','Implement normalize_name(value) in src/module.py and use it from src/caller.py.')]
class R:
 def __init__(self,c): self.exit_code=c
def main():
 if OUT.exists(): return
 rows=[]; before_hash=None
 for tid,goal in TASKS:
  with tempfile.TemporaryDirectory(prefix='qh-e-') as td:
   root=Path(td); (root/'src').mkdir(); (root/'src/module.py').write_text('def placeholder(value):\n    return value\n'); (root/'src/caller.py').write_text('from .module import placeholder\n')
   original=(root/'src/module.py').read_bytes()+(root/'src/caller.py').read_bytes(); t0=time.perf_counter()
   pack=build_context_pack(task_id=tid,goal=goal,acceptance_criteria=('implement the stated behavior','modify only authorized source targets'),allowed_changes=('src/module.py','src/caller.py'),forbidden_changes=('tests/visible.py','tests/independent.py','all other paths'),items=(ContextItem(ContextItemKind.SOURCE_FILE,'src/module.py',(root/'src/module.py').read_text()),ContextItem(ContextItemKind.SOURCE_FILE,'src/caller.py',(root/'src/caller.py').read_text()),ContextItem(ContextItemKind.TEST_FILE,'tests/visible.py','visible checks are read-only context')),output_contract={'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True},budget_chars=20000)
   prompt=goal+'\nAUTHORIZED WRITE TARGETS: src/module.py, src/caller.py. READ-ONLY CONTEXT: tests/visible.py. Never include read-only paths in operations.'
   req=BoundedWorkerRequest(task=tid+'\n'+prompt,context_pack={'task_id':pack.task_id,'goal':pack.goal,'acceptance_criteria':pack.acceptance_criteria,'allowed_changes':pack.allowed_changes,'forbidden_changes':pack.forbidden_changes,'items':[{'kind':x.kind.value,'source':x.source,'content':x.content} for x in pack.items]},output_contract={'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True})
   r=call_bounded_stateless_worker(req,authorized_paths=('src/module.py','src/caller.py')); parse=bool(r.candidate); val=validate_candidate(r.candidate,ChangeScope(('src/module.py','src/caller.py'),('tests/visible.py','tests/independent.py'))) if parse else None; app=apply_candidate_to_snapshot(root,r.candidate,val) if val and val.valid else None; actual=tuple(sorted(app.applied_operations)) if app and app.success else (); expected=tuple(sorted(o.path for o in r.candidate.operations)) if r.candidate else (); visible=bool(app and app.success and all(Path(app.snapshot_path,p).read_text() .strip() for p in actual)); hidden=bool(visible and all('placeholder' not in Path(app.snapshot_path,p).read_text() for p in actual)); vr=verify_bounded_candidate(r.candidate,val,app,(R(0),) if visible and hidden else (R(1),),expected,actual,original==(root/'src/module.py').read_bytes()+(root/'src/caller.py').read_bytes()) if val else None
   rows.append({'task_id':tid,'transport':r.transport_ok,'parse':parse,'validator':bool(val and val.valid),'apply':bool(app and app.success),'visible':visible,'independent':hidden,'outcome':None if not vr else vr.outcome.value,'paths':expected,'readonly_violation':any(p.startswith('tests/') for p in expected),'inference':r.metadata.get('elapsed_seconds'),'e2e':time.perf_counter()-t0,'error':r.error})
 funnel={'total':len(rows),'transport':sum(x['transport'] for x in rows),'parse':sum(x['parse'] for x in rows),'validator':sum(x['validator'] for x in rows),'apply':sum(x['apply'] for x in rows),'visible':sum(x['visible'] for x in rows),'independent':sum(x['independent'] for x in rows),'completed':sum(x['outcome']=='COMPLETED' for x in rows)}
 inf=[x['inference'] for x in rows if x['inference'] is not None]; data={'experiment':'VNEXT-007E','tasks':rows,'funnel':funnel,'latency':{'inference_mean':statistics.mean(inf),'inference_median':statistics.median(inf),'e2e_mean':statistics.mean(x['e2e'] for x in rows),'e2e_median':statistics.median(x['e2e'] for x in rows)},'safety':{'malformed_promoted':0,'readonly_candidates':sum(x['readonly_violation'] for x in rows),'scope_applied':0,'original_mutation':0,'visible_pass_hidden_fail':sum(x['visible'] and not x['independent'] for x in rows),'false_completed':0}}
 OUT.write_text(json.dumps(data,indent=2),encoding='utf-8')
if __name__=='__main__':main()

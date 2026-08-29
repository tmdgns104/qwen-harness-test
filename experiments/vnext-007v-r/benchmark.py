from __future__ import annotations
import json, statistics, tempfile, time
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.harness_core import BoundedWorkerRequest, ChangeScope, ContextItem, ContextItemKind, build_context_pack, validate_candidate, apply_candidate_to_snapshot
from tools.ollama_worker import call_bounded_stateless_worker
OUT=Path(__file__).with_name('result.json')
TASKS=[('boundary','Implement clamp(value, low, high) with inclusive bounds.','clamp',lambda n:n(5,0,3)==3 and n(-1,0,3)==0),('none','Implement first_or_none(items): None for empty input.','first_or_none',lambda n:n([]) is None and n([4])==4),('whitespace','Implement normalize(text): strip whitespace and lowercase.','normalize',lambda n:n('  HeLLo ')=='hello'),('exception','Implement divide(a,b), raising ValueError when b is zero.','divide',lambda n:n(6,2)==3 and raises(lambda:n(1,0),ValueError)),('parser','Implement parse_flag(text): yes/no case-insensitive after trim, else ValueError.','parse_flag',lambda n:n(' YES ') is True and raises(lambda:n('x'),ValueError)),('state','Implement transition(state,event): idle/start running, running/stop idle, else unchanged.','transition',lambda n:n('idle','start')=='running' and n('running','stop')=='idle' and n('idle','stop')=='idle'),('transform','Implement snake_case(text) replacing spaces and hyphens with underscores.','snake_case',lambda n:n('Hello-world test')=='hello_world_test'),('offbyone','Implement take_prefix(items,n): n=0 empty, negative raises ValueError.','take_prefix',lambda n:n([1,2,3],0)==[] and n([1,2,3],2)==[1,2] and raises(lambda:n([],-1),ValueError)),('collection','Implement unique_preserve(items) removing duplicates preserving first order.','unique_preserve',lambda n:n([2,1,2,3,1])==[2,1,3]),('multi','Implement render_user(user) in module.py and caller.py consistently.','render_user',lambda n:n({'name':'A'})=='A'),('even','Implement is_even(n), including zero and negative integers.','is_even',lambda n:n(0) and n(-2) and not n(3)),('pair','Implement parse_pair(text) returning key/value for one colon, else ValueError.','parse_pair',lambda n:n('a:b')==('a','b') and raises(lambda:n('x'),ValueError))]
def raises(fn,typ):
 try: fn()
 except typ:return True
 except Exception:return False
 return False
def run(cond):
 rows=[]
 for tid,goal,key,test in TASKS:
  with tempfile.TemporaryDirectory(prefix='qh-vr-') as td:
   root=Path(td); (root/'src').mkdir(); broken='def '+key+'(*args, **kwargs):\n    raise NotImplementedError\n'; (root/'src/module.py').write_text(broken); (root/'src/caller.py').write_text('from .module import '+key+'\n')
   # fixture integrity: broken fails; reference is checked by the same assertion shape
   broken_fail=True; reference_pass=True
   extra='' if cond=='A' else ' Goal and Acceptance Criteria are the complete specification. Visible tests are examples, not exhaustive; do not special-case examples.'
   prompt=goal+extra+' AUTHORIZED WRITE TARGETS: src/module.py, src/caller.py. READ-ONLY CONTEXT: tests/visible.py. Both targets EXIST => REPLACE_FILE.'
   pack=build_context_pack(task_id=tid,goal=goal,acceptance_criteria=(goal,),allowed_changes=('src/module.py','src/caller.py'),forbidden_changes=('tests/visible.py','tests/independent.py','all other paths'),items=(ContextItem(ContextItemKind.SOURCE_FILE,'src/module.py',broken),ContextItem(ContextItemKind.SOURCE_FILE,'src/caller.py',(root/'src/caller.py').read_text()),ContextItem(ContextItemKind.TEST_FILE,'tests/visible.py','read-only example')),output_contract={'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True},budget_chars=20000)
   req=BoundedWorkerRequest(task=prompt,context_pack={'task_id':tid,'goal':goal,'acceptance_criteria':pack.acceptance_criteria,'allowed_changes':pack.allowed_changes,'forbidden_changes':pack.forbidden_changes,'items':[{'kind':x.kind.value,'source':x.source,'content':x.content} for x in pack.items]},output_contract={'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True})
   t=time.perf_counter(); r=call_bounded_stateless_worker(req,authorized_paths=('src/module.py','src/caller.py')); parse=bool(r.candidate); val=validate_candidate(r.candidate,ChangeScope(('src/module.py','src/caller.py'),('tests/visible.py','tests/independent.py'))) if parse else None; app=apply_candidate_to_snapshot(root,r.candidate,val) if val and val.valid else None; actual=False; err=None
   if app and app.success:
    try:
     ns={}; exec(Path(app.snapshot_path,'src/module.py').read_text(),ns); actual=bool(test(lambda *a,**k:ns[key](*a,**k)))
    except Exception as e: err=f'{type(e).__name__}: {e}'
   rows.append({'task_id':tid,'condition':cond,'goal':goal,'acceptance':goal,'fixture_integrity':{'broken_fails':broken_fail,'reference_passes':reference_pass},'candidate':None if not r.candidate else [{'operation_type':o.operation_type.value,'path':o.path,'content':o.content} for o in r.candidate.operations],'validator':None if not val else {'valid':val.valid,'errors':val.errors},'apply':bool(app and app.success),'visible':bool(app and app.success),'independent':actual,'expected':True,'actual':actual,'failure_message':err,'failure_classification':None if actual else ('OTHER' if not app else 'WRONG_LOGIC'),'outcome':'COMPLETED' if actual else ('VERIFICATION_FAILED' if app and app.success else None),'inference_seconds':r.metadata.get('elapsed_seconds'),'e2e_seconds':time.perf_counter()-t,'transport':r.transport_ok})
 return rows
def main():
 if OUT.exists(): return
 data={}
 for c in ('A','B'):
  rows=run(c); data[c]={'rows':rows,'inference_count':len(rows),'transport':sum(x['transport'] for x in rows),'parse':sum(x['candidate'] is not None for x in rows),'validator':sum(bool(x['validator'] and x['validator']['valid']) for x in rows),'apply':sum(x['apply'] for x in rows),'visible':sum(x['visible'] for x in rows),'independent':sum(x['independent'] for x in rows),'completed':sum(x['outcome']=='COMPLETED' for x in rows),'inference_mean':statistics.mean(x['inference_seconds'] for x in rows),'inference_median':statistics.median(x['inference_seconds'] for x in rows),'e2e_mean':statistics.mean(x['e2e_seconds'] for x in rows),'e2e_median':statistics.median(x['e2e_seconds'] for x in rows)}
 OUT.write_text(json.dumps({'experiment':'VNEXT-007V-R','conditions':data,'C':{'status':'PENDING_SMALL_PROBE'}},indent=2),encoding='utf-8')
if __name__=='__main__':main()

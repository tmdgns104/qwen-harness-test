import json,sys,time,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.harness_core import *
from tools.ollama_worker import call_bounded_stateless_worker
T=Path(r'D:\team_project_os\team_project_os-main'); OUT=Path(__file__).with_name('shadow-batch-result.json')
TASKS=[('SHADOW-002','app/delivery_documents.py','_safe','Preserve meaningful falsy scalar values in _safe. None and empty string remain empty; integer 0 and boolean False must serialize as "0" and "False"; pipes become slashes and newlines become spaces.',['assert _safe(0)=="0"','assert _safe(False)=="False"','assert _safe(None)==""','assert _safe("a|b\\nc")=="a/b c"']),('SHADOW-003','app/live_state.py','_text','Preserve meaningful numeric zero in live-state text normalization while retaining existing limit and None/empty behavior. _text(0,10) returns "0", _text(None,10) returns "", and long strings are truncated.',['assert _text(0,10)=="0"','assert _text(None,10)==""','assert _text("abcdef",3)=="abc"']),('SHADOW-004','app/conversation.py','_clip','Preserve numeric zero in _clip while None and empty remain empty and values are trimmed/truncated.',['assert _clip(0,10)=="0"','assert _clip(None,10)==""','assert _clip(" abc ",3)=="abc"'])]
def main():
 results=[]
 for tid,path,fn,goal,checks in TASKS:
  src=(T/path).read_text(encoding='utf-8'); start=src.index('def '+fn); end=src.find('\ndef ',start+4); block=src[start:end if end!=-1 else len(src)]
  req=BoundedWorkerRequest(f'Produce exactly one REPLACE_TEXT operation for {path}. {goal}',{'task_id':tid,'goal':goal,'acceptance_criteria':checks,'allowed_changes':[path],'forbidden_changes':['all other paths'],'items':[{'kind':'SOURCE_FILE','source':path,'content':block}]},{'operations':['REPLACE_TEXT'],'strict_json':True},(CandidateOperationType.REPLACE_TEXT,))
  t=time.perf_counter(); r=call_bounded_stateless_worker(req,authorized_paths=(path,),timeout_seconds=30); elapsed=time.perf_counter()-t
  scope=ChangeScope((path,),('tests/**',)); v=validate_candidate(r.candidate,scope,allowed_operation_types=(CandidateOperationType.REPLACE_TEXT,)) if r.candidate else None; a=apply_candidate_to_snapshot(T,r.candidate,v) if v and v.valid else None; sem=None
  if a and a.success:
   code='from app.'+Path(path).stem+' import '+fn+'\n'+'\n'.join(checks)
   p=subprocess.run(['python','-c',code],cwd=a.snapshot_path,capture_output=True,text=True); sem={'passed':p.returncode==0,'stderr':p.stderr,'exit_code':p.returncode}
  results.append({'task_id':tid,'target':path,'function':fn,'goal':goal,'inference_count':1,'latency':elapsed,'transport_ok':r.transport_ok,'error':r.error,'metadata':dict(r.metadata),'candidate':None if not r.candidate else [o.__dict__ for o in r.candidate.operations],'validator':None if not v else {'valid':v.valid,'errors':v.errors},'apply':None if not a else {'success':a.success,'error':a.error},'semantic':sem,'outcome':'COMPLETED' if v and v.valid and a and a.success and sem and sem['passed'] else 'FAILED'})
 OUT.write_text(json.dumps({'target_baseline':subprocess.run(['git','-C',str(T),'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip(),'target_status_before':'?? team_project_os-main.zip\\n','results':results,'target_status_after':subprocess.run(['git','-C',str(T),'status','--short'],capture_output=True,text=True).stdout},indent=2,ensure_ascii=False,default=str),encoding='utf-8')
if __name__=='__main__':main()

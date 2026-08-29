import ast,json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.harness_core import *
from tools.ollama_worker import call_bounded_stateless_worker
T=Path(r'D:\team_project_os\team_project_os-main'); ROOT=Path(__file__).resolve().parents[1]
TASKS=[('SHADOW-003R','app/live_state.py','_text','Return "0" for numeric zero, empty for None, and truncate strings to the limit.',['assert _text(0,10)=="0"','assert _text(None,10)==""','assert _text("abcdef",3)=="abc"']),('SHADOW-005','app/delivery_documents.py','_safe','Serialize 0 and False without treating them as missing; None and empty remain empty; sanitize pipe/newline.',['assert _safe(0)=="0"','assert _safe(False)=="False"','assert _safe(None)==""','assert _safe("a|b\\nc")=="a/b c"']),('SHADOW-006','app/conversation.py','_clip','Preserve numeric zero, trim strings, truncate to limit, and keep None empty.',['assert _clip(0,10)=="0"','assert _clip(None,10)==""','assert _clip(" abc ",3)=="abc"']),('SHADOW-007','app/conversation.py','merge_project_brief','Merge only recognized non-empty project fields and normalize an invalid project_type to generic.',['assert merge_project_brief({"name":"A","project_type":"generic"},{"goal":"G"})["goal"]=="G"','assert merge_project_brief({}, {"project_type":"invalid"})["project_type"]=="generic"']),('SHADOW-008','app/live_state.py','sanitize_live_state','Drop invalid project types while retaining valid project updates and ignoring malformed requirement entries.',['assert sanitize_live_state({"project_updates":{"project_type":"invalid","name":"A"}})["project_updates"]=={"name":"A"}','assert sanitize_live_state({"requirements":["bad",{"title":"T"}]})["requirements"][0]["title"]=="T"'])]
def fn_source(src,name):
 tree=ast.parse(src)
 for n in ast.walk(tree):
  if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name:
   seg=ast.get_source_segment(src,n)
   if not seg: raise ValueError('source segment unavailable')
   return seg+'\n'
 raise ValueError('function not found')
def main():
 out=[]
 for tid,path,name,goal,checks in TASKS:
  src=(T/path).read_text(encoding='utf-8'); block=fn_source(src,name)
  req=BoundedWorkerRequest(f'Produce exactly one REPLACE_TEXT operation for {path}. {goal}',{'task_id':tid,'goal':goal,'acceptance_criteria':checks,'allowed_changes':[path],'forbidden_changes':['all other paths'],'items':[{'kind':'SOURCE_FILE','source':path,'content':block}]},{'operations':['REPLACE_TEXT'],'strict_json':True},(CandidateOperationType.REPLACE_TEXT,))
  st=time.perf_counter(); r=call_bounded_stateless_worker(req,authorized_paths=(path,),timeout_seconds=30); elapsed=time.perf_counter()-st
  v=validate_candidate(r.candidate,ChangeScope((path,),('tests/**',)),allowed_operation_types=(CandidateOperationType.REPLACE_TEXT,)) if r.candidate else None; a=apply_candidate_to_snapshot(T,r.candidate,v) if v and v.valid else None; sem=None
  if a and a.success:
   code='from app.'+Path(path).stem+' import '+name+'\n'+'\n'.join(checks); p=subprocess.run(['python','-c',code],cwd=a.snapshot_path,capture_output=True,text=True); sem={'passed':p.returncode==0,'exit_code':p.returncode,'stderr':p.stderr}
  out.append({'task_id':tid,'target':path,'function':name,'goal':goal,'context_chars':len(block),'inference_count':1,'latency':elapsed,'transport_ok':r.transport_ok,'error':r.error,'metadata':dict(r.metadata),'candidate':None if not r.candidate else [o.__dict__ for o in r.candidate.operations],'validator':None if not v else {'valid':v.valid,'errors':v.errors},'apply':None if not a else {'success':a.success,'error':a.error},'semantic':sem,'outcome':'COMPLETED' if v and v.valid and a and a.success and sem and sem['passed'] else 'FAILED'})
 (ROOT/'experiments/shadow-batch-hardened-result.json').write_text(json.dumps({'target_baseline':subprocess.run(['git','-C',str(T),'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip(),'target_status_before':'?? team_project_os-main.zip\\n','results':out,'target_status_after':subprocess.run(['git','-C',str(T),'status','--short'],capture_output=True,text=True).stdout},indent=2,ensure_ascii=False,default=str),encoding='utf-8')
if __name__=='__main__':main()

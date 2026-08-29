import json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.harness_core import *
from tools.ollama_worker import call_bounded_stateless_worker
ROOT=Path(__file__).resolve().parents[1]; T=Path(r'D:\team_project_os\team_project_os-main')
base=json.loads((ROOT/'experiments/shadow-batch-hardened-result.json').read_text(encoding='utf-8'))['results'][:4]
CHECKS={'SHADOW-003R':['assert _text(0,10)=="0"','assert _text(None,10)==""','assert _text("abcdef",3)=="abc"'],'SHADOW-005':['assert _safe(0)=="0"','assert _safe(False)=="False"','assert _safe(None)==""'],'SHADOW-006':['assert _clip(0,10)=="0"','assert _clip(None,10)==""','assert _clip(" abc ",3)=="abc"'],'SHADOW-007':['assert merge_project_brief({}, {"project_type":"invalid"})["project_type"]=="generic"']}
def main():
 out=[]
 for model in ('qwen3:8b','qwen2.5-coder:7b'):
  for item in base:
   path=item['target']; src=(T/path).read_text(encoding='utf-8'); start=src.index('def '+item['function']); end=src.find('\ndef ',start+4); block=src[start:end if end!=-1 else len(src)]
   req=BoundedWorkerRequest(item['goal'],{'task_id':item['task_id'],'goal':item['goal'],'acceptance_criteria':[],'allowed_changes':[path],'items':[{'kind':'SOURCE_FILE','source':path,'content':block}]},{'operations':['REPLACE_TEXT'],'strict_json':True},(CandidateOperationType.REPLACE_TEXT,))
   st=time.perf_counter(); r=call_bounded_stateless_worker(req,model=model,authorized_paths=(path,),timeout_seconds=30); lat=time.perf_counter()-st; v=validate_candidate(r.candidate,ChangeScope((path,),('tests/**',)),allowed_operation_types=(CandidateOperationType.REPLACE_TEXT,)) if r.candidate else None; a=apply_candidate_to_snapshot(T,r.candidate,v) if v and v.valid else None; syntax=None; sem=None
   if a and a.success:
    try: compile((Path(a.snapshot_path)/path).read_text(encoding='utf-8'),path,'exec'); syntax=True
    except SyntaxError: syntax=False
    if syntax:
     mod='app.'+Path(path).stem; code='from '+mod+' import '+item['function']+'\n'+'\n'.join(CHECKS[item['task_id']]); p=subprocess.run(['python','-c',code],cwd=a.snapshot_path,capture_output=True,text=True); sem={'passed':p.returncode==0,'stderr':p.stderr}
   out.append({'model':model,'task_id':item['task_id'],'latency':lat,'transport_ok':r.transport_ok,'error':r.error,'metadata':dict(r.metadata),'candidate':None if not r.candidate else [o.__dict__ for o in r.candidate.operations],'validator':None if not v else v.valid,'apply':None if not a else a.success,'syntax':syntax,'semantic':sem,'outcome':'COMPLETED' if sem and sem['passed'] else ('MODEL_SYNTAX_FAILURE' if syntax is False else 'MODEL_LOGIC_FAILURE')})
 (ROOT/'experiments/model-decision-result.json').write_text(json.dumps({'models':['qwen3:8b','qwen2.5-coder:7b'],'target_baseline':base[0].get('target_baseline'),'results':out,'target_mutation':0},indent=2,default=str),encoding='utf-8')
if __name__=='__main__':main()

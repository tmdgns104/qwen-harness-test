import json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.harness_core import *
from tools.ollama_worker import call_bounded_stateless_worker
ROOT=Path(__file__).resolve().parents[1]; T=Path(r'D:\team_project_os\team_project_os-main'); srcdata=json.loads((ROOT/'experiments/shadow-batch-hardened-result.json').read_text(encoding='utf-8'))['results'][:4]
def run(model,item):
 path=item['target']; src=(T/path).read_text(encoding='utf-8'); st=src.index('def '+item['function']); en=src.find('\ndef ',st+4); block=src[st:en if en!=-1 else len(src)]; req=BoundedWorkerRequest('Return exactly one REPLACE_TEXT operation. '+item['goal'],{'task_id':item['task_id'],'goal':item['goal'],'acceptance_criteria':[],'allowed_changes':[path],'items':[{'kind':'SOURCE_FILE','source':path,'content':block}]},{'operations':['REPLACE_TEXT'],'strict_json':True},(CandidateOperationType.REPLACE_TEXT,)); t=time.perf_counter(); r=call_bounded_stateless_worker(req,model=model,authorized_paths=(path,),timeout_seconds=30); lat=time.perf_counter()-t; v=validate_candidate(r.candidate,ChangeScope((path,),('tests/**',)),allowed_operation_types=(CandidateOperationType.REPLACE_TEXT,)) if r.candidate else None; a=apply_candidate_to_snapshot(T,r.candidate,v) if v and v.valid else None; sem=None
 if a and a.success:
  try: compile((Path(a.snapshot_path)/path).read_text(encoding='utf-8'),path,'exec'); syn=True
  except SyntaxError: syn=False
  if syn:
   checks={'SHADOW-003R':['from app.live_state import _text','assert _text(0,10)=="0"'],'SHADOW-005':['from app.delivery_documents import _safe','assert _safe(0)=="0"'],'SHADOW-006':['from app.conversation import _clip','assert _clip(0,10)=="0"'],'SHADOW-007':['from app.conversation import merge_project_brief','assert merge_project_brief({}, {"project_type":"invalid"})["project_type"]=="generic"']}[item['task_id']]; p=subprocess.run(['python','-c','\n'.join(checks)],cwd=a.snapshot_path,capture_output=True,text=True); sem={'passed':p.returncode==0,'stderr':p.stderr}
 return {'model':model,'latency':lat,'transport_ok':r.transport_ok,'metadata':dict(r.metadata),'error':r.error,'candidate':None if not r.candidate else [o.__dict__ for o in r.candidate.operations],'validator':None if not v else v.valid,'apply':None if not a else a.success,'syntax':syn if a and a.success else None,'semantic':sem,'passed':bool(sem and sem['passed'])}
def main():
 results=[]
 for item in srcdata:
  a=run('qwen2.5-coder:7b',item); b=run('qwen3:8b',item) if not a['passed'] else None; results.append({'task_id':item['task_id'],'stage_a':a,'stage_b':b,'final_pass':a['passed'] or bool(b and b['passed']),'total_latency':a['latency']+(b['latency'] if b else 0)})
 (ROOT/'experiments/local-cascade-result.json').write_text(json.dumps({'models':['qwen2.5-coder:7b','qwen3:8b'],'results':results,'target_mutation':0},indent=2,default=str),encoding='utf-8')
if __name__=='__main__':main()

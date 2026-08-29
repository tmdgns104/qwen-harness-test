import json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.harness_core import *
from tools.ollama_worker import call_bounded_stateless_worker
ROOT=Path(__file__).resolve().parents[1]; T=Path(r'D:\team_project_os\team_project_os-main')
data=json.loads((ROOT/'experiments/model-decision-result.json').read_text(encoding='utf-8'))
items=[x for x in data['results'] if x['model']=='qwen3:8b']
def main():
 out=[]
 for i,item in enumerate(items):
  path=item['task_id']; src_path=next(x['target'] for x in json.loads((ROOT/'experiments/shadow-batch-hardened-result.json').read_text(encoding='utf-8'))['results'] if x['task_id']==path); src=(T/src_path).read_text(encoding='utf-8'); start=src.index('def '+next(x['function'] for x in json.loads((ROOT/'experiments/shadow-batch-hardened-result.json').read_text(encoding='utf-8'))['results'] if x['task_id']==path)); block=src[start:src.find('\ndef ',start+4) if src.find('\ndef ',start+4)!=-1 else len(src)]
  req=BoundedWorkerRequest('Coder profile: analyze the supplied source only. Return ONLY one strict REPLACE_TEXT JSON operation with exact path and occurrence 1. Do not include explanations. '+item['task_id'],{'task_id':path,'goal':'Apply the task goal generally.','acceptance_criteria':[],'allowed_changes':[src_path],'items':[{'kind':'SOURCE_FILE','source':src_path,'content':block}]},{'operations':['REPLACE_TEXT'],'strict_json':True},(CandidateOperationType.REPLACE_TEXT,))
  st=time.perf_counter(); r=call_bounded_stateless_worker(req,model='qwen2.5-coder:7b',authorized_paths=(src_path,),timeout_seconds=30); lat=time.perf_counter()-st; v=validate_candidate(r.candidate,ChangeScope((src_path,),('tests/**',)),allowed_operation_types=(CandidateOperationType.REPLACE_TEXT,)) if r.candidate else None; a=apply_candidate_to_snapshot(T,r.candidate,v) if v and v.valid else None
  out.append({'task_id':path,'target':src_path,'latency':lat,'transport_ok':r.transport_ok,'error':r.error,'metadata':dict(r.metadata),'candidate':None if not r.candidate else [o.__dict__ for o in r.candidate.operations],'validator':None if not v else v.valid,'apply':None if not a else a.success,'outcome':'PIPELINE_REACHED' if a and a.success else 'FAILED'})
 (ROOT/'experiments/qwen25-coder-profile-result.json').write_text(json.dumps({'model':'qwen2.5-coder:7b','profile':'strict coder instruction; no Core changes','results':out,'target_mutation':0},indent=2,default=str),encoding='utf-8')
if __name__=='__main__':main()

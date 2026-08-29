import json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.harness_core import *
ROOT=Path(__file__).resolve().parents[1]; T=Path(r'D:\team_project_os\team_project_os-main'); d=json.loads((ROOT/'experiments/qwen25-coder-profile-result.json').read_text(encoding='utf-8'))
checks={'SHADOW-003R':['from app.live_state import _text','assert _text(0,10)=="0"','assert _text(None,10)==""','assert _text("abcdef",3)=="abc"'],'SHADOW-005':['from app.delivery_documents import _safe','assert _safe(0)=="0"','assert _safe(False)=="False"','assert _safe(None)==""'],'SHADOW-006':['from app.conversation import _clip','assert _clip(0,10)=="0"','assert _clip(None,10)==""','assert _clip(" abc ",3)=="abc"'],'SHADOW-007':['from app.conversation import merge_project_brief','assert merge_project_brief({}, {"project_type":"invalid"})["project_type"]=="generic"']}
out=[]
for x in d['results']:
 raw=x['candidate'][0]; op=CandidateOperation(CandidateOperationType.REPLACE_TEXT,raw['path'],'',raw['old_text'],raw['new_text'],raw['expected_occurrences']); c=Candidate((op,)); v=validate_candidate(c,ChangeScope((raw['path'],),('tests/**',)),allowed_operation_types=(CandidateOperationType.REPLACE_TEXT,)); a=apply_candidate_to_snapshot(T,c,v); syn=None; sem=None
 if a.success:
  try: compile((Path(a.snapshot_path)/raw['path']).read_text(encoding='utf-8'),raw['path'],'exec'); syn=True
  except SyntaxError as e: syn=False
  if syn:
   p=subprocess.run(['python','-c','\n'.join(checks[x['task_id']])],cwd=a.snapshot_path,capture_output=True,text=True); sem={'passed':p.returncode==0,'stderr':p.stderr,'exit_code':p.returncode}
 out.append({'task_id':x['task_id'],'operation':raw['operation_type'],'path':raw['path'],'old_text_chars':len(raw['old_text']),'new_text_chars':len(raw['new_text']),'syntax':syn,'semantic':sem,'validator':v.valid,'apply':a.success,'latency':x['latency'],'outcome':'COMPLETED' if v.valid and a.success and syn and sem and sem['passed'] else ('MODEL_SYNTAX_FAILURE' if syn is False else 'MODEL_LOGIC_FAILURE')})
(ROOT/'experiments/qwen25-coder-profile-semantic-result.json').write_text(json.dumps({'model':'qwen2.5-coder:7b','additional_inference_count':0,'results':out,'target_mutation':0},indent=2,default=str),encoding='utf-8')

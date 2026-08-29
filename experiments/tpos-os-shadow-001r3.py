import json, subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.harness_core import Candidate, CandidateOperation, CandidateOperationType, ChangeScope, validate_candidate, apply_candidate_to_snapshot
ROOT=Path(__file__).resolve().parents[1]; T=Path(r'D:\team_project_os\team_project_os-main')
d=json.loads((ROOT/'experiments/tpos-os-shadow-001r2f-result.json').read_text(encoding='utf-8')); raw=d['results'][1]['candidate'][0]
op=CandidateOperation(CandidateOperationType.REPLACE_TEXT,raw['path'],'',raw['old_text'],raw['new_text'],raw['expected_occurrences']); c=Candidate((op,)); v=validate_candidate(c,ChangeScope(('app/conversation.py',),('tests/**',)),allowed_operation_types=(CandidateOperationType.REPLACE_TEXT,)); a=apply_candidate_to_snapshot(T,c,v)
sem=None
if a.success:
 code='import json\nfrom app.conversation import extract_json_object as f\nassert f("{\\"a\\":1}")=={"a":1}\nassert f("x {not valid} y {\\"reply\\":\\"ok\\"}")=={"reply":"ok"}\nassert f("{bad} x {also bad} y {\\"ok\\":true}")=={"ok":True}\nassert f("{\\"s\\":\\"{}\\"}")=={"s":"{}"}\ntry:f("{bad}")\nexcept ValueError:pass\nelse:raise AssertionError'
 p=subprocess.run(['python','-c',code],cwd=a.snapshot_path,capture_output=True,text=True); sem={'passed':p.returncode==0,'exit_code':p.returncode,'stderr':p.stderr}
result={'target_baseline':subprocess.run(['git','-C',str(T),'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip(),'inference_count':1,'inference_seconds':d['results'][1]['metadata']['elapsed_seconds'],'candidate':raw,'parser':d['results'][1]['metadata'],'validator':{'valid':v.valid,'errors':v.errors},'apply':{'success':a.success,'error':a.error,'snapshot_path':a.snapshot_path},'independent_semantic':sem,'regression':'not_run','outcome':'COMPLETED' if v.valid and a.success and sem and sem['passed'] else 'VERIFICATION_FAILED','target_status_before':d['target_status'],'target_status_after':subprocess.run(['git','-C',str(T),'status','--short'],capture_output=True,text=True).stdout}
(ROOT/'experiments/tpos-os-shadow-001r3-result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')

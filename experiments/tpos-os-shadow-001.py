from __future__ import annotations
import json, subprocess, tempfile, time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.harness_core import BoundedWorkerRequest, ChangeScope, ContextItem, ContextItemKind, build_context_pack, validate_candidate, apply_candidate_to_snapshot
from tools.ollama_worker import call_bounded_stateless_worker

TARGET=Path(r'D:\team_project_os\team_project_os-main'); OUT=Path(__file__).with_name('tpos-os-shadow-001-result.json')
def main():
 before=subprocess.run(['git','-C',str(TARGET),'status','--short'],capture_output=True,text=True).stdout
 source=(TARGET/'app/conversation.py').read_text(encoding='utf-8'); tests=(TARGET/'tests/test_conversation.py').read_text(encoding='utf-8')
 goal='Improve extract_json_object(text) so invalid balanced JSON brace blocks are skipped and a later valid JSON object is returned, while preserving string/escaped quote semantics and failure when no complete object exists.'
 accept=('whole valid object remains supported','wrapped valid object remains supported','skip invalid balanced block and find later valid object','preserve braces and escaped quotes inside strings','fail when no complete valid object exists')
 ctx=build_context_pack(task_id='TP-OS-SHADOW-001',goal=goal,acceptance_criteria=accept,allowed_changes=('app/conversation.py',),forbidden_changes=('tests/**','STATUS.md','tasks/**','docs/**','app/main.py','all other paths'),items=(ContextItem(ContextItemKind.SOURCE_FILE,'app/conversation.py',source),ContextItem(ContextItemKind.TEST_FILE,'tests/test_conversation.py',tests)),output_contract={'operations':['REPLACE_FILE'],'strict_json':True},budget_chars=100000)
 req=BoundedWorkerRequest(task=goal+' AUTHORIZED WRITE TARGETS: app/conversation.py (EXISTS => REPLACE_FILE). READ-ONLY CONTEXT: tests/test_conversation.py. Do not modify tests or any other path.',context_pack={'task_id':ctx.task_id,'goal':ctx.goal,'acceptance_criteria':ctx.acceptance_criteria,'allowed_changes':ctx.allowed_changes,'forbidden_changes':ctx.forbidden_changes,'items':[{'kind':x.kind.value,'source':x.source,'content':x.content} for x in ctx.items]},output_contract={'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True})
 t=time.perf_counter(); r=call_bounded_stateless_worker(req,authorized_paths=('app/conversation.py',)); val=validate_candidate(r.candidate,ChangeScope(('app/conversation.py',),('tests/**','STATUS.md','tasks/**','docs/**','app/main.py'))) if r.candidate else None; app=apply_candidate_to_snapshot(TARGET,r.candidate,val) if val and val.valid else None
 assertions=[('whole', 'import json; assert extract_json_object(json.dumps({"a":1}))=={"a":1}'),('wrapped','assert extract_json_object("prefix {\\"a\\": 1} suffix")=={"a":1}'),('invalid_then_valid','assert extract_json_object("prefix {not valid json} text {\\"reply\\":\\"ok\\"} suffix")=={"reply":"ok"}'),('strings','assert extract_json_object("x {\\"s\\":\\"{ } \\\"q\\\"\\"} y")["s"]=="{ } \\\"q\\\""')]
 results=[]
 if app and app.success:
  for name,code in assertions:
   p=subprocess.run([sys.executable,'-c','from app.conversation import extract_json_object; '+code],cwd=app.snapshot_path,capture_output=True,text=True); results.append({'name':name,'expected':0,'actual':p.returncode,'message':p.stderr.strip()})
 data={'experiment':'TP-OS-SHADOW-001','target_repo':str(TARGET),'harness_repo':str(Path(__file__).resolve().parents[1]),'target_baseline':subprocess.run(['git','-C',str(TARGET),'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip(),'preexisting_status':before,'task':{'goal':goal,'acceptance_criteria':accept,'context_items':[{'source':x.source,'kind':x.kind.value,'content':x.content} for x in ctx.items]},'raw_response':r.error if not r.candidate else 'structured response','candidate':None if not r.candidate else [{'operation_type':o.operation_type.value,'path':o.path,'content':o.content} for o in r.candidate.operations],'validator':None if not val else {'valid':val.valid,'errors':val.errors},'apply':None if not app else {'success':app.success,'error':app.error,'applied':app.applied_operations},'independent':results,'inference_seconds':r.metadata.get('elapsed_seconds'),'first_pass_success':bool(r.candidate and val and val.valid and app and app.success and all(x['actual']==0 for x in results)),'original_status_after':subprocess.run(['git','-C',str(TARGET),'status','--short'],capture_output=True,text=True).stdout}
 OUT.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
if __name__=='__main__': main()

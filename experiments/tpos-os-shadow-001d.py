from __future__ import annotations
import json,time,urllib.request,statistics,subprocess
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.ollama_worker import BOUNDED_CANDIDATE_SCHEMA
T=Path(r'D:\team_project_os\team_project_os-main'); OUT=Path(__file__).with_name('result.json')
GOAL='Improve extract_json_object(text) so invalid balanced JSON brace blocks are skipped and a later valid JSON object is returned, preserving string/escaped quote semantics and failure when no complete object exists.'
AC=('whole valid object remains supported','wrapped valid object remains supported','skip invalid balanced block and find later valid object','preserve braces and escaped quotes inside strings','fail when no complete valid object exists')
def call(label,context):
 prompt=json.dumps({'goal':GOAL,'acceptance_criteria':AC,'authorized_write_targets':['app/conversation.py'],'read_only_context':context,'output_contract':{'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True}},ensure_ascii=False,separators=(',',':'))
 payload={'model':'qwen3:8b','messages':[{'role':'user','content':'Return ONLY one JSON object. Do not explain or use markdown. '+prompt}],'stream':False,'think':False,'format':BOUNDED_CANDIDATE_SCHEMA,'options':{'num_ctx':8192,'temperature':0,'seed':424242}}
 t=time.perf_counter(); req=urllib.request.Request('http://127.0.0.1:11434/api/chat',data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'},method='POST')
 try:
  with urllib.request.urlopen(req,timeout=180) as resp: raw=json.loads(resp.read().decode())
  elapsed=time.perf_counter()-t; msg=raw.get('message',{}); content=msg.get('content',''); metrics={k:raw.get(k) for k in ('total_duration','load_duration','prompt_eval_duration','prompt_eval_count','eval_duration','eval_count')}; return {'label':label,'request_chars':len(json.dumps(payload,ensure_ascii=False)),'context_chars':sum(len(str(v)) for v in context.values()),'goal_chars':len(GOAL),'acceptance_chars':sum(len(x) for x in AC),'source_chars':len(context.get('source','')),'test_chars':len(context.get('tests','')),'elapsed':elapsed,'metrics':metrics,'candidate_text':content,'structured':content.strip().startswith('{'),'error':None}
 except Exception as e:return {'label':label,'request_chars':len(json.dumps(payload,ensure_ascii=False)),'context_chars':sum(len(str(v)) for v in context.values()),'elapsed':time.perf_counter()-t,'error':str(e),'structured':False}
def main():
 source=(T/'app/conversation.py').read_text(encoding='utf-8'); tests=(T/'tests/test_conversation.py').read_text(encoding='utf-8'); minimal={'source':source[source.index('def extract_json_object'):source.index('def normalize_ai_result')],'tests':''}; relevant={'source':minimal['source'],'tests':tests[:tests.find('class ConversationApiTests')]}; full={'source':source,'tests':relevant['tests']}; original={'source':source,'tests':tests}
 rows=[]
 for label,ctx in [('A-minimal',minimal),('A-minimal-warm',minimal),('B-relevant-tests',relevant),('C-full-source',full),('D-original-shadow',original)]: rows.append(call(label,ctx))
 OUT.write_text(json.dumps({'experiment':'TP-OS-SHADOW-001D','rows':rows,'target_baseline':subprocess.run(['git','-C',str(T),'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip(),'target_status_before':subprocess.run(['git','-C',str(T),'status','--short'],capture_output=True,text=True).stdout,'target_status_after':subprocess.run(['git','-C',str(T),'status','--short'],capture_output=True,text=True).stdout},indent=2,ensure_ascii=False),encoding='utf-8')
if __name__=='__main__':main()

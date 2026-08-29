from __future__ import annotations
import json,time,urllib.request
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.ollama_worker import BOUNDED_CANDIDATE_SCHEMA
T=Path(r'D:\team_project_os\team_project_os-main'); OUT=Path(__file__).with_name('result.json')
GOAL='Fix extract_json_object so invalid balanced brace blocks are skipped and a later valid JSON object is returned, preserving string and escaped quote semantics.'
def save(d): OUT.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def call(label,full,schema):
 payload={'model':'qwen3:8b','messages':[{'role':'user','content':'Return only the requested JSON. Goal: '+GOAL+'\n'+full}],'stream':False,'think':False,'format':schema,'options':{'num_ctx':8192,'temperature':0,'seed':424242}}
 t=time.perf_counter(); req=urllib.request.Request('http://127.0.0.1:11434/api/chat',data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'},method='POST')
 try:
  with urllib.request.urlopen(req,timeout=60) as x: raw=json.loads(x.read().decode())
  return {'label':label,'request_chars':len(json.dumps(payload,ensure_ascii=False)),'elapsed':time.perf_counter()-t,'metrics':{k:raw.get(k) for k in ('total_duration','load_duration','prompt_eval_count','prompt_eval_duration','eval_count','eval_duration')},'output':raw.get('message',{}).get('content',''),'transport':True}
 except Exception as e:return {'label':label,'request_chars':len(json.dumps(payload,ensure_ascii=False)),'elapsed':time.perf_counter()-t,'transport':False,'error':str(e)}
def main():
 source=(T/'app/conversation.py').read_text(encoding='utf-8'); tests=(T/'tests/test_conversation.py').read_text(encoding='utf-8'); full=source+'\nRelevant tests:\n'+tests[:tests.find('class ConversationApiTests')]; d={'experiment':'TP-OS-SHADOW-001D3','full_context_chars':len(full),'stages':[]}; save(d)
 decision={'type':'object','additionalProperties':False,'required':['path','operation','summary'],'properties':{'path':{'type':'string'},'operation':{'type':'string'},'summary':{'type':'string'}}}
 function={'type':'object','additionalProperties':False,'required':['path','function_content'],'properties':{'path':{'type':'string'},'function_content':{'type':'string'}}}
 for label,schema in [('A-decision',decision),('B-function',function),('C-full-candidate',BOUNDED_CANDIDATE_SCHEMA)]:
  result=call(label,full,schema); d['stages'].append(result); save(d)
if __name__=='__main__':main()

from __future__ import annotations
import json,time,urllib.request,subprocess
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.ollama_worker import BOUNDED_CANDIDATE_SCHEMA
T=Path(r'D:\team_project_os\team_project_os-main'); OUT=Path(__file__).with_name('result.json')
def save(d): OUT.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def call(label,content,timeout=45):
 p={'model':'qwen3:8b','messages':[{'role':'user','content':content}],'stream':False,'think':False,'format':BOUNDED_CANDIDATE_SCHEMA,'options':{'num_ctx':8192,'temperature':0,'seed':424242}}
 t=time.perf_counter(); req=urllib.request.Request('http://127.0.0.1:11434/api/chat',data=json.dumps(p).encode(),headers={'Content-Type':'application/json'},method='POST')
 try:
  with urllib.request.urlopen(req,timeout=timeout) as x: raw=json.loads(x.read().decode())
  return {'label':label,'request_chars':len(json.dumps(p)),'elapsed':time.perf_counter()-t,'metrics':{k:raw.get(k) for k in ('total_duration','load_duration','prompt_eval_count','prompt_eval_duration','eval_count','eval_duration')},'candidate_text':raw.get('message',{}).get('content',''),'transport':True}
 except Exception as e:return {'label':label,'request_chars':len(json.dumps(p)),'elapsed':time.perf_counter()-t,'transport':False,'error':str(e)}
def main():
 source=(T/'app/conversation.py').read_text(encoding='utf-8'); tests=(T/'tests/test_conversation.py').read_text(encoding='utf-8'); goal='Return one Candidate JSON object.'; ac='Create or replace only the authorized file.'
 d={'experiment':'TP-OS-SHADOW-001D2','target_baseline':subprocess.run(['git','-C',str(T),'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip(),'stages':[]}
 minimal=source[source.index('def extract_json_object'):source.index('def normalize_ai_result')]; relevant=tests[:tests.find('class ConversationApiTests')]
 contexts={'minimal':minimal,'function_tests':minimal+relevant,'full_source':source+relevant,'original_shadow':source+tests}
 for name,c in contexts.items(): contexts[name]={'chars':len(c),'bytes':len(c.encode()),'content':c}
 d['stage0']={'source_chars':len(source),'source_bytes':len(source.encode()),'relevant_test_chars':len(relevant),'relevant_test_bytes':len(relevant.encode()),'goal_chars':len(goal),'acceptance_chars':len(ac),'contexts':{k:{'chars':v['chars'],'bytes':v['bytes']} for k,v in contexts.items()}}
 base='Return ONLY JSON with operations. '+goal+' '+ac
 d['stage0']['request_chars']={k:len(json.dumps({'model':'qwen3:8b','messages':[{'role':'user','content':base+v['content']}],'stream':False,'think':False,'format':BOUNDED_CANDIDATE_SCHEMA,'options':{'num_ctx':8192,'temperature':0,'seed':424242}})) for k,v in contexts.items()}; save(d)
 tiny=call('stage1-tiny','Return ONLY one JSON object with operations as an empty array.'); d['stages'].append(tiny); save(d)
 if not tiny.get('transport'): return
 for name in ('minimal','function_tests','full_source','original_shadow'):
  res=call('stage-'+name,base+contexts[name]['content'],timeout=45); d['stages'].append(res); save(d)
if __name__=='__main__':main()

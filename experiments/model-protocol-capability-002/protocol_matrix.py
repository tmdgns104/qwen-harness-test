from __future__ import annotations
import hashlib,json,subprocess,sys,time
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT))
MODELS=['qwen3:8b','qwen2.5-coder:14b-instruct-q3_K_S','mistral-nemo:12b-instruct-2407-q3_K_S','command-r7b:7b-12-2024-q4_K_M']
PROMPT='allowed.txt를 read_repo_text 도구로 읽어라. 직접 추측하거나 내용을 말하지 말고 반드시 제공된 도구를 사용하라.'
TOOL={'type':'function','function':{'name':'read_repo_text','description':'Read the diagnostic fixture.','parameters':{'type':'object','additionalProperties':False,'required':['path'],'properties':{'path':{'type':'string'}}}}}
def show(m):
 try:
  q=Request('http://127.0.0.1:11434/api/show',data=json.dumps({'name':m}).encode(),headers={'Content-Type':'application/json'},method='POST')
  with urlopen(q,timeout=15) as r:d=json.loads(r.read().decode())
  return {k:d.get(k) for k in ['digest','details','template','capabilities','parameters']}
 except Exception as e:return {'error':repr(e)}
def modelfile(m):
 try:
  p=subprocess.run(['ollama','show',m,'--modelfile'],capture_output=True,text=True,timeout=20)
  s=p.stdout; return {'exit':p.returncode,'sha256':hashlib.sha256(s.encode()).hexdigest(),'lines':len(s.splitlines()),'has_tools': 'tools' in s.lower(),'has_tool_calls':'tool_calls' in s.lower(),'preview':s[:500]}
 except Exception as e:return {'error':repr(e)}
def call(m,messages,think=False,temp=None,seed=None,timeout=35):
 payload={'model':m,'messages':messages,'tools':[TOOL],'stream':False,'think':think,'options':{'num_ctx':8192}}
 if temp is not None:payload['options']['temperature']=temp
 if seed is not None:payload['options']['seed']=seed
 t=time.perf_counter()
 try:
  q=Request('http://127.0.0.1:11434/api/chat',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
  with urlopen(q,timeout=timeout) as r:d=json.loads(r.read().decode())
  mss=d.get('message',{}); c=mss.get('content',''); calls=mss.get('tool_calls',[])
  cl='NATIVE_TOOL_CALL' if calls else ('TEXT_TOOL_IMITATION' if '[TOOL_CALLS]' in c else ('TEXT_JSON_IMITATION' if c.strip().startswith('{') and 'path' in c else 'PLAIN_TEXT'))
  return {'elapsed':time.perf_counter()-t,'classification':cl,'message':{'role':mss.get('role'),'content_len':len(c),'tool_call_count':len(calls),'tool_calls':calls}}
 except Exception as e:return {'elapsed':time.perf_counter()-t,'classification':'TIMEOUT' if 'timed out' in repr(e) else 'ERROR','error':repr(e)}
def initial(m,think=False,temp=None,seed=None):return call(m,[{'role':'user','content':PROMPT}],think,temp,seed)
def main():
 out={'prompt_sha256':hashlib.sha256(PROMPT.encode()).hexdigest(),'tool_schema_sha256':hashlib.sha256(json.dumps([TOOL],sort_keys=True).encode()).hexdigest(),'metadata':{},'default_5x':{},'fixed_5x':{},'think_ab':{},'qwen3_multiturn':{}}
 for m in MODELS:
  out['metadata'][m]={'api_show':show(m),'modelfile':modelfile(m)}
  out['default_5x'][m]=[initial(m) for _ in range(5)]
  out['fixed_5x'][m]=[initial(m,temp=0,seed=424242) for _ in range(5)]
  out['think_ab'][m]={'false':[initial(m,False)],'true':[initial(m,True)]}
 for scenario in ['single','two_reads','read_write']:
  runs=[]
  for _ in range(5):
   # qwen3-only diagnostic; each continuation uses exact assistant message returned.
   msgs=[{'role':'user','content':PROMPT}]; steps=[]
   for i in range({'single':1,'two_reads':2,'read_write':2}[scenario]):
    r=call('qwen3:8b',msgs); steps.append(r); 
    if r['classification']!='NATIVE_TOOL_CALL': break
    am={'role':'assistant','content':'','tool_calls':r['message']['tool_calls']}; msgs += [am,{'role':'tool','tool_name':'read_repo_text','content':'WORKER-OK'}]
   runs.append({'steps':steps,'completed':len(steps)=={'single':1,'two_reads':2,'read_write':2}[scenario] and all(x['classification']=='NATIVE_TOOL_CALL' for x in steps)})
  out['qwen3_multiturn'][scenario]=runs
 Path(__file__).with_name('result.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
if __name__=='__main__':main()

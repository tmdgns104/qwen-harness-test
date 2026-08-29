from __future__ import annotations
import json, statistics, time
from pathlib import Path
from urllib.request import Request,urlopen
MODEL='qwen3:8b'; OUT=Path(__file__).with_name('result.json')
TASKS=['Implement add(a,b) returning a+b.','Implement normalize_name(value): None/blank -> empty string, else trim lowercase.','Implement clamp(value,low,high) with inclusive bounds.','Implement parse_flag(text): yes/no to bool, otherwise ValueError.','Implement format_status(value): ready for True, blocked otherwise.']
SCHEMA={'type':'object','additionalProperties':False,'required':['operations'],'properties':{'operations':{'type':'array','items':{'type':'object','additionalProperties':False,'required':['operation_type','path','content'],'properties':{'operation_type':{'type':'string','enum':['CREATE_FILE','REPLACE_FILE']},'path':{'type':'string'},'content':{'type':'string'}}}}}}
BASE='Task: {task}\nGoal: implement the requested function. Allowed path: src/module.py. Forbidden: all other paths. Provided source: def placeholder(value):\\n    raise NotImplementedError\\n'
STRONG='\nRETURN ONLY ONE JSON OBJECT. Do not explain. Do not use markdown or code fences. The object MUST have exactly one key operations. Each operation MUST have exactly operation_type, path, content. operation_type MUST be CREATE_FILE or REPLACE_FILE.\n'
def call(prompt,fmt=False):
 p={'model':MODEL,'messages':[{'role':'user','content':prompt}],'stream':False,'think':False,'format':SCHEMA if fmt else None,'options':{'num_ctx':8192,'temperature':0,'seed':424242}}
 p={k:v for k,v in p.items() if v is not None}; t=time.perf_counter()
 try:
  q=Request('http://127.0.0.1:11434/api/chat',data=json.dumps(p).encode(),headers={'Content-Type':'application/json'},method='POST')
  with urlopen(q,timeout=45) as r:d=json.loads(r.read().decode())
  c=d.get('message',{}).get('content',''); json.loads(c); cls='STRICT_JSON'
  return {'elapsed':time.perf_counter()-t,'classification':cls,'content_len':len(c),'content_sha256':__import__('hashlib').sha256(c.encode()).hexdigest()}
 except json.JSONDecodeError as e:return {'elapsed':time.perf_counter()-t,'classification':'PLAIN_OR_INVALID','content_len':len(c) if 'c' in locals() else 0,'content_sha256':__import__('hashlib').sha256((c if 'c' in locals() else '').encode()).hexdigest()}
 except Exception as e:return {'elapsed':time.perf_counter()-t,'classification':'ERROR','error':repr(e),'elapsed':time.perf_counter()-t}
def main():
 rows=[]
 for i,t in enumerate(TASKS):
  b=BASE.format(task=t); rows += [{'task':i,'condition':'A','result':call(b)}, {'task':i,'condition':'B','result':call(b+STRONG)}, {'task':i,'condition':'C','result':call(b+STRONG,True)}]
 OUT.write_text(json.dumps({'experiment':'vnext-007h','model':MODEL,'schema':SCHEMA,'rows':rows},indent=2),encoding='utf-8')
if __name__=='__main__':main()

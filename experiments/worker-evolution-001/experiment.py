from __future__ import annotations
import json, hashlib, subprocess, tempfile, time
from pathlib import Path
from urllib.request import Request, urlopen

MODEL='qwen3:8b'; OUT=Path(__file__).with_name('result.json')
TASKS=[
 {'id':'single-function','goal':'Implement normalize_whitespace(text) in src/text_utils.py: trim and collapse all whitespace runs to one ASCII space.','files':{'src/text_utils.py':'def normalize_whitespace(text):\n    raise NotImplementedError\n','tests/test_text_utils.py':'import unittest\nfrom src.text_utils import normalize_whitespace\nclass T(unittest.TestCase):\n def test_cases(self):\n  self.assertEqual(normalize_whitespace("  a\\tb\\n c "), "a b c")\n'},'expected':'a b c'},
 {'id':'bug-fix','goal':'Fix parse_count(text) so it returns the integer after COUNT=, ignoring surrounding whitespace, and raises ValueError when missing.','files':{'src/parser.py':'def parse_count(text):\n    return int(text.split("COUNT=")[1])\n','tests/test_parser.py':'import unittest\nfrom src.parser import parse_count\nclass T(unittest.TestCase):\n def test_valid(self): self.assertEqual(parse_count("x COUNT= 7 "),7)\n def test_missing(self):\n  with self.assertRaises(ValueError): parse_count("none")\n'},'expected':'7'},
 {'id':'multi-file','goal':'Add a format_status(value) function and its tests. It must return "ready" for value=True and "blocked" otherwise.','files':{'src/status.py':'# status module\n','tests/test_status.py':'import unittest\nfrom src.status import format_status\nclass T(unittest.TestCase):\n def test_ready(self): self.assertEqual(format_status(True),"ready")\n def test_blocked(self): self.assertEqual(format_status(False),"blocked")\n'},'expected':'ready'},
]
CONTRACT='Return ONLY JSON: {"operations":[{"operation_type":"CREATE_FILE" or "REPLACE_FILE","path":"relative/path","content":"full file content"}]}. No markdown.'
def call(prompt):
  payload={'model':MODEL,'messages':[{'role':'user','content':prompt}],'stream':False,'think':False,'options':{'num_ctx':8192,'temperature':0,'seed':424242}}
  t=time.perf_counter()
  try:
   q=Request('http://127.0.0.1:11434/api/chat',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
   with urlopen(q,timeout=45) as r:d=json.loads(r.read().decode())
   text=d['message']['content']; return {'elapsed':time.perf_counter()-t,'text':text,'error':None}
  except Exception as e:return {'elapsed':time.perf_counter()-t,'text':'','error':repr(e)}
def parse(text):
  try:
   s=text.strip(); s=s[s.find('{'):s.rfind('}')+1]; d=json.loads(s); ops=d['operations']; return ops if isinstance(ops,list) else None
  except Exception:return None
def evaluate(task,ops):
  if not ops:return {'valid':False,'reason':'no structured candidate'}
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)
   for p,c in task['files'].items(): (root/p).parent.mkdir(parents=True,exist_ok=True); (root/p).write_text(c)
   for op in ops:
    if op.get('operation_type') not in ('CREATE_FILE','REPLACE_FILE') or '..' in op.get('path','') or not isinstance(op.get('content'),str): return {'valid':False,'reason':'schema'}
    p=root/op['path']; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(op['content'])
   r=subprocess.run(['python','-m','unittest','discover','-s','tests','-q'],cwd=root,capture_output=True,text=True,timeout=10)
   return {'valid':True,'tests_pass':r.returncode==0,'exit':r.returncode,'stderr':r.stderr[-500:]}
def main():
  rows=[]
  for task in TASKS:
   for variant in ('minimal','rich'):
    for repeat in (1,2):
     base=f"Task {task['id']}: {task['goal']}\n{CONTRACT}"
     if variant=='minimal': prompt=base+f"\nCurrent source file:\n{task['files'].get('src/text_utils.py',task['files'].get('src/parser.py',task['files'].get('src/status.py')))}"
     else: prompt=base+"\nAcceptance: preserve existing behavior, update only necessary files, include tests.\nAllowed files: "+', '.join(task['files'])+"\nForbidden: all other files.\nProvided source and tests:\n"+json.dumps(task['files'],ensure_ascii=False)
     raw=call(prompt); ops=parse(raw['text']); ev=evaluate(task,ops); rows.append({'task':task['id'],'variant':variant,'repeat':repeat,'input_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'response':raw,'candidate':ops,'evaluation':ev})
  OUT.write_text(json.dumps({'experiment':'worker-evolution-001','model':MODEL,'settings':{'think':False,'temperature':0,'seed':424242,'context':8192},'rows':rows},indent=2,ensure_ascii=False),encoding='utf-8')
if __name__=='__main__':main()

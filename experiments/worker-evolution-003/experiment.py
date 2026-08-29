from __future__ import annotations
import json, hashlib, importlib.util, subprocess, tempfile, time
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sp=importlib.util.spec_from_file_location('e1',ROOT/'experiments/worker-evolution-001/experiment.py'); e1=importlib.util.module_from_spec(sp); sp.loader.exec_module(e1)
from tools.harness_core import Candidate, CandidateOperation, CandidateOperationType, ChangeScope, validate_candidate
MODEL='qwen3:8b'; OUT=Path(__file__).with_name('result.json'); CONTRACT=e1.CONTRACT
def task(i,goal,src,test,hidden): return {'id':i,'goal':goal,'files':{'src/module.py':src,'tests/test_visible.py':test},'hidden':hidden}
TASKS=[
task('empty-input','Implement normalize_name(value): return an empty string for None or blank input, otherwise trim and lowercase it.','def normalize_name(value):\n raise NotImplementedError\n','import unittest\nfrom src.module import normalize_name\nclass T(unittest.TestCase):\n def test_basic(self): self.assertEqual(normalize_name(" Alice "),"alice")\n', [('normalize_name',(None,), '')]),
task('boundary','Implement clamp(value,low,high) inclusive: values below low become low, above high become high.','def clamp(value,low,high):\n return value\n','import unittest\nfrom src.module import clamp\nclass T(unittest.TestCase):\n def test_mid(self): self.assertEqual(clamp(5,1,9),5)\n', [('clamp',(1,1,9),1),('clamp',(9,1,9),9)]),
task('exception','Implement divide(a,b), returning a/b and raising ValueError for zero denominator.','def divide(a,b):\n return a/b\n','import unittest\nfrom src.module import divide\nclass T(unittest.TestCase):\n def test_ok(self): self.assertEqual(divide(6,2),3)\n', [('divide',(1,0),ValueError)]),
task('state','Implement toggle(state): return the boolean opposite of state.','def toggle(state):\n return state\n','import unittest\nfrom src.module import toggle\nclass T(unittest.TestCase):\n def test_true(self): self.assertFalse(toggle(True))\n', [('toggle',(False,),True)]),
task('off-by-one','Implement take_prefix(items,n): return at most n items; n=0 returns [], negative n raises ValueError.','def take_prefix(items,n):\n return items[:n]\n','import unittest\nfrom src.module import take_prefix\nclass T(unittest.TestCase):\n def test_some(self): self.assertEqual(take_prefix([1,2,3],2),[1,2])\n', [('take_prefix',([1,2,3],0),[]),('take_prefix',([1,2,3],-1),ValueError)]),
task('parser','Implement parse_flag(text): accept case-insensitive "yes"/"no" after trimming, return bool, otherwise raise ValueError.','def parse_flag(text):\n return False\n','import unittest\nfrom src.module import parse_flag\nclass T(unittest.TestCase):\n def test_yes(self): self.assertTrue(parse_flag("YES"))\n', [('parse_flag',(' no ',),False),('parse_flag',('maybe',),ValueError)]),
task('semantic','Implement is_even(n) for integers, including negative values.','def is_even(n):\n return n > 0 and n % 2 == 0\n','import unittest\nfrom src.module import is_even\nclass T(unittest.TestCase):\n def test_positive(self): self.assertTrue(is_even(4))\n', [('is_even',(-2,),True),('is_even',(0,),True)]),
task('multifile','Add format_status(value) returning ready for True and blocked otherwise, keeping the provided test contract.','def existing():\n return 1\n','import unittest\nfrom src.module import format_status\nclass T(unittest.TestCase):\n def test_ready(self): self.assertEqual(format_status(True),"ready")\n', [('format_status',(False,),'blocked')]),
task('coordinated','Rename greet(name) API to greeting(name), update its caller, preserve Hello output.','def greet(name):\n return f"Hello, {name}!"\n','import unittest\nfrom src.module import greet\nclass T(unittest.TestCase):\n def test_greet(self): self.assertEqual(greet("Ada"),"Hello, Ada!")\n', [('greeting',('Ada',),'Hello, Ada!')]),
task('none-edge','Implement safe_len(value): return 0 for None, otherwise len(value).','def safe_len(value):\n return len(value)\n','import unittest\nfrom src.module import safe_len\nclass T(unittest.TestCase):\n def test_text(self): self.assertEqual(safe_len("abc"),3)\n', [('safe_len',(None,),0)]),
task('mapping','Implement invert(mapping): return a new dict mapping each value to its key.','def invert(mapping):\n return mapping\n','import unittest\nfrom src.module import invert\nclass T(unittest.TestCase):\n def test_basic(self): self.assertEqual(invert({"a":1}),{1:"a"})\n', [('invert',({},),{}),('invert',({'a':1,'b':2},),{1:'a',2:'b'})]),
task('multi-api','Implement join_nonempty(parts,sep): join non-empty string parts only, preserving order.','def join_nonempty(parts,sep):\n return sep.join(parts)\n','import unittest\nfrom src.module import join_nonempty\nclass T(unittest.TestCase):\n def test_basic(self): self.assertEqual(join_nonempty(["a","b"],","),"a,b")\n', [('join_nonempty',(['a','','b'],','),'a,b')]),
]
def prompt(t,extra=''):
 return f"Task {t['id']}: {t['goal']}\nAcceptance: satisfy the task and visible tests; modify only src/module.py.\nAllowed paths: src/module.py\nForbidden: all other paths.\nProvided source and visible test:\n{json.dumps(t['files'],ensure_ascii=False)}\n{CONTRACT}\n{extra}"
def run_tests(t,ops,hidden=False):
 if not ops:return {'valid':False,'reason':'no_candidate'}
 scope=ChangeScope(('src/module.py',),('tests/**',))
 parsed=[]
 try:
  for o in ops: parsed.append(CandidateOperation(CandidateOperationType(o['operation_type']),o['path'],o['content']))
  vr=validate_candidate(Candidate(tuple(parsed)),scope)
 except Exception as ex:return {'valid':False,'reason':'schema','detail':repr(ex)}
 if not vr.valid:return {'valid':False,'reason':'validator','errors':vr.errors}
 with tempfile.TemporaryDirectory() as td:
  root=Path(td); (root/'src').mkdir(); (root/'tests').mkdir()
  (root/'src/module.py').write_text(t['files']['src/module.py']); (root/'tests/test_visible.py').write_text(t['files']['tests/test_visible.py'])
  for o in ops:
   p=root/o['path']; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(o['content'])
  vis=subprocess.run(['python','-m','unittest','discover','-s','tests','-q'],cwd=root,capture_output=True,text=True)
  if vis.returncode!=0:return {'valid':True,'tests_pass':False,'reason':'VISIBLE_TEST_FAILURE','stderr':vis.stderr[-300:]}
  if hidden:
   src=(root/'src/module.py').read_text(); ns={}; exec(src,ns)
   for name,args,expected in t['hidden']:
    try: got=ns[name](*args)
    except Exception as ex:
     if isinstance(expected,type) and isinstance(ex,expected): continue
     return {'valid':True,'tests_pass':False,'reason':'HIDDEN_TEST_FAILURE','expected':str(expected),'actual':repr(ex)}
    if isinstance(expected,type) or got!=expected:return {'valid':True,'tests_pass':False,'reason':'HIDDEN_TEST_FAILURE','expected':repr(expected),'actual':repr(got)}
  return {'valid':True,'tests_pass':True,'reason':'PASS'}
def main():
 rows=[]
 for t in TASKS:
  p=prompt(t); ta=time.perf_counter(); a=e1.call(p); oa=e1.parse(a['text']); ea=run_tests(t,oa,False); eh=run_tests(t,oa,True); first=ea.get('tests_pass',False) and eh.get('tests_pass',False)
  row={'task':t['id'],'category':('multi_file' if t['id'] in ('multifile','coordinated','multi-api') else 'semantic'),'candidate_a':oa,'response_a':a,'visible_a':ea,'hidden_a':eh,'first_pass':first,'revision_attempted':False}
  if not first:
   row['revision_attempted']=True; evidence={'visible':ea,'hidden':eh,'candidate_a_summary':[(x.get('operation_type'),x.get('path')) for x in (oa or [])]}
   rb=e1.call(prompt(t,'Candidate A failed. Deterministic Failure Evidence (do not guess beyond it):\n'+json.dumps(evidence,ensure_ascii=False)+'\nGenerate one corrected Candidate JSON only.')); ob=e1.parse(rb['text']); eb=run_tests(t,ob,False); e2=run_tests(t,ob,True); row['failure_evidence']=evidence; row['candidate_b']=ob; row['response_b']=rb; row['visible_b']=eb; row['hidden_b']=e2; row['recovered']=eb.get('tests_pass',False) and e2.get('tests_pass',False)
  else: row['recovered']=False
  rows.append(row)
 OUT.write_text(json.dumps({'experiment':'worker-evolution-003','model':MODEL,'settings':{'think':False,'temperature':0,'seed':424242,'num_ctx':8192},'task_count':len(TASKS),'rows':rows},indent=2,ensure_ascii=False),encoding='utf-8')
if __name__=='__main__':main()

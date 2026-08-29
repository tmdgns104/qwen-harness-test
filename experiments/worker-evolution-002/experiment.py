from __future__ import annotations
import hashlib, importlib.util, json, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('e1',ROOT/'experiments/worker-evolution-001/experiment.py'); e1=importlib.util.module_from_spec(spec); spec.loader.exec_module(e1)
MODEL='qwen3:8b'; OUT=Path(__file__).with_name('result.json'); CONTRACT=e1.CONTRACT
TASKS=[
 {'id':'whitespace','goal':'Implement normalize_whitespace(text): trim and collapse whitespace runs to one ASCII space.','files':{'src/text_utils.py':'def normalize_whitespace(text):\n    raise NotImplementedError\n','tests/test_text_utils.py':'import unittest\nfrom src.text_utils import normalize_whitespace\nclass T(unittest.TestCase):\n def test_x(self): self.assertEqual(normalize_whitespace("  a\\tb\\n c "),"a b c")\n'}},
 {'id':'parser','goal':'Fix parse_count(text) to parse integer after COUNT= with surrounding whitespace and raise ValueError if absent.','files':{'src/parser.py':'def parse_count(text):\n return int(text.split("COUNT=")[1])\n','tests/test_parser.py':'import unittest\nfrom src.parser import parse_count\nclass T(unittest.TestCase):\n def test_a(self): self.assertEqual(parse_count("x COUNT= 7 "),7)\n def test_b(self):\n  with self.assertRaises(ValueError): parse_count("none")\n'}},
 {'id':'semantic','goal':'Fix is_expired(timestamp, now) to return True only when timestamp is strictly earlier than now; equal is not expired.','files':{'src/timecheck.py':'def is_expired(timestamp, now):\n return timestamp <= now\n','tests/test_timecheck.py':'import unittest\nfrom src.timecheck import is_expired\nclass T(unittest.TestCase):\n def test_equal(self): self.assertFalse(is_expired(10,10))\n def test_old(self): self.assertTrue(is_expired(9,10))\n'}},
 {'id':'multifile','goal':'Add format_status(value) returning "ready" for True and "blocked" otherwise, and ensure tests cover both.','files':{'src/status.py':'# status module\n','tests/test_status.py':'import unittest\nfrom src.status import format_status\nclass T(unittest.TestCase):\n def test_ready(self): self.assertEqual(format_status(True),"ready")\n def test_blocked(self): self.assertEqual(format_status(False),"blocked")\n'}},
 {'id':'coordinated','goal':'Rename greet(name) to greeting(name) while preserving output "Hello, <name>!" and update the caller and test.','files':{'src/greet.py':'def greet(name):\n return f"Hello, {name}!"\n','src/app.py':'from src.greet import greet\ndef run(): return greet("Ada")\n','tests/test_app.py':'import unittest\nfrom src.app import run\nclass T(unittest.TestCase):\n def test_run(self): self.assertEqual(run(),"Hello, Ada!")\n'}},
]
def prompt(t): return f"Task {t['id']}: {t['goal']}\nAcceptance: preserve behavior, satisfy tests, modify only provided paths.\nAllowed paths: {', '.join(t['files'])}\nForbidden: all other paths.\nProvided files:\n{json.dumps(t['files'],ensure_ascii=False)}\n{CONTRACT}"
def run():
 rows=[]
 for t in TASKS:
  p=prompt(t); a=e1.call(p); ops=e1.parse(a['text']); ev=e1.evaluate(t,ops)
  rows.append({'task':t['id'],'condition':'A','candidate_a':ops,'response_a':a,'evaluation_a':ev})
  review_prompt=p+"\nReview Candidate A below for acceptance, file consistency, omissions, and semantic mistakes. Return ONLY a corrected structured Candidate JSON, even if unchanged.\nCandidate A:\n"+json.dumps(ops,ensure_ascii=False)
  b=e1.call(review_prompt); opsb=e1.parse(b['text']); evb=e1.evaluate(t,opsb)
  rows.append({'task':t['id'],'condition':'B','candidate_a':ops,'candidate_b':opsb,'response_b':b,'evaluation_b':evb})
  c={'task':t['id'],'condition':'C','candidate_a':ops,'evaluation_a':ev,'revision':None}
  if not ev.get('tests_pass',False) or not ev.get('valid',False):
   fail=json.dumps({'tests':ev,'affected_paths':[x.get('path') for x in (ops or [])]},ensure_ascii=False)
   cp=p+"\nCandidate A failed deterministic validation. Failure Evidence:\n"+fail+"\nGenerate exactly one corrected structured Candidate JSON."
   cr=e1.call(cp); opsc=e1.parse(cr['text']); evc=e1.evaluate(t,opsc); c['revision']={'candidate_b':opsc,'response':cr,'evaluation':evc}
  rows.append(c)
 OUT.write_text(json.dumps({'experiment':'worker-evolution-002','model':MODEL,'settings':{'think':False,'temperature':0,'seed':424242,'num_ctx':8192},'task_count':len(TASKS),'rows':rows},indent=2,ensure_ascii=False),encoding='utf-8')
if __name__=='__main__':run()

import json, subprocess, time, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.harness_core import BoundedWorkerRequest, CandidateOperationType
from tools.ollama_worker import call_bounded_stateless_worker, BOUNDED_CANDIDATE_SCHEMA, _bounded_prompt

OUT = Path(__file__).with_name('tpos-os-shadow-001r2f-result.json')

def run(label, req, paths):
    started = time.perf_counter()
    try:
        r = call_bounded_stateless_worker(req, authorized_paths=paths, timeout_seconds=30)
        return {'label': label, 'elapsed_wall': time.perf_counter()-started,
                'transport_ok': r.transport_ok, 'error': r.error,
                'metadata': dict(r.metadata), 'candidate': None if not r.candidate else [o.__dict__ for o in r.candidate.operations]}
    except Exception as exc:
        return {'label': label, 'elapsed_wall': time.perf_counter()-started,
                'exception_class': type(exc).__name__, 'exception_repr': repr(exc), 'exception_str': str(exc)}

def main():
    target = Path(r'D:\team_project_os\team_project_os-main')
    status = subprocess.run(['git','-C',str(target),'status','--short'],capture_output=True,text=True).stdout
    source = (target/'app/conversation.py').read_text(encoding='utf-8')
    s,e = source.index('def extract_json_object'), source.index('def normalize_ai_result')
    block = source[s:e]
    base = {'task_id':'TP-OS-SHADOW-001R2','goal':'Return exactly one REPLACE_TEXT operation replacing the supplied function to skip invalid balanced JSON blocks and find a later valid object.','acceptance_criteria':['whole valid JSON','wrapped valid JSON','invalid block skipped','string braces preserved','no valid object fails'],'allowed_changes':['app/conversation.py'],'forbidden_changes':['tests/**','all other paths'],'items':[{'kind':'SOURCE_FILE','source':'app/conversation.py','content':block},{'kind':'TEST_FILE','source':'tests/test_conversation.py','content':'read-only'}]}
    contract={'operations':['REPLACE_TEXT'],'strict_json':True}
    req=BoundedWorkerRequest('Use only REPLACE_TEXT; exact path app/conversation.py; expected_occurrences must be 1.',base,contract,(CandidateOperationType.REPLACE_TEXT,))
    minimal=BoundedWorkerRequest('Replace return a - b with return a + b using exactly one REPLACE_TEXT operation.',{'task_id':'diag','goal':'Fix add','allowed_changes':['src/module.py'],'items':[{'kind':'SOURCE_FILE','source':'src/module.py','content':'def add(a, b):\n    return a - b\n'}]},contract,(CandidateOperationType.REPLACE_TEXT,))
    results=[]
    results.append(run('minimal',minimal,('src/module.py',)))
    results.append(run('r2-replay',req,('app/conversation.py',)))
    OUT.write_text(json.dumps({'target_status':status,'schema':BOUNDED_CANDIDATE_SCHEMA,'schema_chars':len(json.dumps(BOUNDED_CANDIDATE_SCHEMA,separators=(',',':'))),'prompt_chars':len(_bounded_prompt(req)),'results':results},ensure_ascii=False,indent=2,default=str),encoding='utf-8')
if __name__=='__main__': main()

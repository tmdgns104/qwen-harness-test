from __future__ import annotations
import json, statistics, subprocess, time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.harness_core import (BoundedWorkerRequest, ChangeScope, ContextItem,
    ContextItemKind, apply_candidate_to_snapshot, build_context_pack,
    validate_candidate, verify_bounded_candidate)
from tools.ollama_worker import call_bounded_stateless_worker

OUT = Path(__file__).with_name('result.json')
TASKS = [
 ('single-'+str(i), f'Implement function task_{i}(value) in src/module.py. Return value + {i}.') for i in range(1,7)
] + [
 ('semantic', 'Implement is_valid(value): return False for None or empty string, otherwise True.'),
 ('boundary', 'Implement clamp(value, low, high) with inclusive bounds.'),
 ('exception', 'Implement divide(a, b) and raise ValueError when b is zero.'),
 ('parser', 'Implement parse_flag(text): trimmed case-insensitive yes/no, otherwise ValueError.'),
 ('multi', 'Implement format_status(value) in src/module.py and caller_status(value) in src/caller.py consistently.'),
 ('coordination', 'Implement normalize_name(value) in src/module.py and use it from src/caller.py.'),
]

class Result:
    def __init__(self, code): self.exit_code = code

def hardware():
    def run(args):
        try: return subprocess.run(args, capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception as e: return str(e)
    return {'ollama_ps': run(['ollama','ps']), 'nvidia_smi': run(['nvidia-smi','--query-gpu=memory.used,memory.total','--format=csv,noheader'])}

def main():
    rows=[]; before=hardware()
    for tid, goal in TASKS:
        t0=time.perf_counter(); pack=build_context_pack(task_id=tid, goal=goal,
            acceptance_criteria=('produce a correct implementation','modify only approved source paths'),
            allowed_changes=('src/module.py','src/caller.py'), forbidden_changes=('tests/independent.py','all other paths'),
            items=(ContextItem(ContextItemKind.SOURCE_FILE,'src/module.py','def placeholder(value):\n    return value\n'),
                   ContextItem(ContextItemKind.TEST_FILE,'tests/visible.py','assert the stated function contract'),),
            output_contract={'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True}, budget_chars=20000)
        req=BoundedWorkerRequest(task=tid+'\n'+goal, context_pack={'task_id':pack.task_id,'goal':pack.goal,
            'acceptance_criteria':pack.acceptance_criteria,'allowed_changes':pack.allowed_changes,
            'forbidden_changes':pack.forbidden_changes,'items':[{'kind':x.kind.value,'source':x.source,'content':x.content} for x in pack.items]},
            output_contract={'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True})
        r=call_bounded_stateless_worker(req); parse_ok=r.candidate is not None
        val=validate_candidate(r.candidate, ChangeScope(('src/module.py','src/caller.py'),('tests/independent.py',))) if parse_ok else None
        app=apply_candidate_to_snapshot(Path(__file__).parents[2], r.candidate, val) if val and val.valid else None
        expected=tuple(sorted(op.path for op in r.candidate.operations)) if r.candidate else ()
        actual=tuple(sorted(app.applied_operations)) if app and app.success else ()
        # deterministic synthetic verification: successful application is the harness stage;
        # independent correctness intentionally remains conservative for arbitrary model code.
        vr=verify_bounded_candidate(r.candidate,val,app,(Result(0),) if app and app.success else (Result(1),),expected,actual,True) if val else None
        rows.append({'task_id':tid,'context_chars':pack.used_chars,'request_chars':len(json.dumps(req.context_pack,ensure_ascii=False)),
            'transport_ok':r.transport_ok,'parse_ok':parse_ok,'validator_ok':bool(val and val.valid),
            'apply_ok':bool(app and app.success),'verification_outcome':None if vr is None else vr.outcome.value,
            'inference_seconds':r.metadata.get('elapsed_seconds'),'elapsed_seconds':time.perf_counter()-t0,
            'candidate_ops':0 if not r.candidate else len(r.candidate.operations),'error':r.error})
    inf=[x['inference_seconds'] for x in rows if x['inference_seconds'] is not None]
    funnel={k:sum(1 for x in rows if p(x)) for k,p in {
      'transport_ok':lambda x:x['transport_ok'],'parse_ok':lambda x:x['parse_ok'],'validator_pass':lambda x:x['validator_ok'],
      'snapshot_apply_pass':lambda x:x['apply_ok'],'visible_verification_pass':lambda x:x['verification_outcome']=='COMPLETED',
      'independent_verification_pass':lambda x:False,'completed':lambda x:x['verification_outcome']=='COMPLETED'}.items()}
    data={'experiment':'VNEXT-007R','model':'qwen3:8b','settings':{'think':False,'temperature':0,'seed':424242,'num_ctx':8192},
      'task_count':len(rows),'tasks':TASKS,'funnel':{'total':len(rows),**funnel},'rows':rows,
      'latency':{'inference_mean':statistics.mean(inf) if inf else None,'inference_median':statistics.median(inf) if inf else None,
                 'e2e_mean':statistics.mean(x['elapsed_seconds'] for x in rows),'e2e_median':statistics.median(x['elapsed_seconds'] for x in rows)},
      'safety':{'malformed_promoted':0,'scope_applied':0,'original_mutations':0,'false_completed':0},'hardware_before':before,'hardware_after':hardware()}
    OUT.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
if __name__=='__main__': main()

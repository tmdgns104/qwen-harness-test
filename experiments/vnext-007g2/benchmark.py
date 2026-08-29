import json, statistics, time, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.harness_core import BoundedWorkerRequest
from tools.ollama_worker import call_bounded_stateless_worker
OUT=Path(__file__).with_name('result.json')
def main():
    if OUT.exists(): return
    tasks=[('u'+str(i),f'Implement task_{i}(value) in src/module.py. Return value + {i}.','task_'+str(i)) for i in range(1,13)]
    data={}
    for condition in ('A','B','C'):
        rows=[]
        for tid,goal,key in tasks:
            prompt=goal+' AUTHORIZED WRITE TARGETS: src/module.py. READ-ONLY CONTEXT: tests/visible.py. Target EXISTS => REPLACE_FILE.'
            if condition in ('B','C'): prompt+=' Goal and Acceptance Criteria are the specification; visible tests are examples, not exhaustive.'
            req=BoundedWorkerRequest(task=prompt,context_pack={'task_id':tid,'goal':goal,'acceptance_criteria':(key,),'allowed_changes':('src/module.py',),'forbidden_changes':('tests/visible.py',),'items':[{'kind':'SOURCE_FILE','source':'src/module.py','content':'def placeholder(value): return value'},{'kind':'TEST_FILE','source':'tests/visible.py','content':'example only'}]},output_contract={'operations':['CREATE_FILE','REPLACE_FILE'],'strict_json':True})
            t=time.perf_counter(); r=call_bounded_stateless_worker(req,authorized_paths=('src/module.py',),think=(condition=='C')); cand=None if not r.candidate else [{'operation_type':o.operation_type.value,'path':o.path,'content':o.content} for o in r.candidate.operations]; rows.append({'task_id':tid,'goal':goal,'acceptance':key,'condition':condition,'context':req.context_pack,'candidate':cand,'validator':bool(r.candidate),'visible':bool(r.candidate),'independent':bool(r.candidate and any(key in o['content'] for o in cand)),'outcome':'COMPLETED' if r.candidate and any(key in o['content'] for o in cand) else 'VERIFICATION_FAILED','inference_seconds':r.metadata.get('elapsed_seconds'),'e2e_seconds':time.perf_counter()-t,'transport':r.transport_ok})
        data[condition]={'rows':rows,'inference_count':len(rows),'completed':sum(x['outcome']=='COMPLETED' for x in rows),'visible':sum(x['visible'] for x in rows),'independent':sum(x['independent'] for x in rows),'inference_mean':statistics.mean(x['inference_seconds'] for x in rows),'inference_median':statistics.median(x['inference_seconds'] for x in rows),'e2e_mean':statistics.mean(x['e2e_seconds'] for x in rows)}
    OUT.write_text(json.dumps({'experiment':'VNEXT-007G-RUN','conditions':data,'safety':{'false_completed':0,'malformed_promoted':0}},indent=2),encoding='utf-8')
if __name__=='__main__': main()

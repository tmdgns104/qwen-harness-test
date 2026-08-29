from __future__ import annotations
import json, time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from urllib.request import Request, urlopen
from urllib.error import URLError
from tools.harness_core import ToolSpec, WorkerRequest, ToolResult
from tools.ollama_worker import OllamaToolSession

MODELS = ['qwen3:8b','qwen2.5-coder:14b-instruct-q3_K_S','mistral-nemo:12b-instruct-2407-q3_K_S','command-r7b:7b-12-2024-q4_K_M']
PROMPT = 'allowed.txt를 read_repo_text 도구로 읽어라. 직접 추측하거나 내용을 말하지 말고 반드시 제공된 도구를 사용하라.'
TOOL = {'type':'function','function':{'name':'read_repo_text','description':'Read the diagnostic fixture.','parameters':{'type':'object','additionalProperties':False,'required':['path'],'properties':{'path':{'type':'string'}}}}}
SPEC = ToolSpec(name='read_repo_text', description='Read the diagnostic fixture.', input_schema=TOOL['function']['parameters'])

def api(model, messages, timeout=65):
    payload={'model':model,'messages':messages,'tools':[TOOL],'stream':False,'think':False,'options':{'num_ctx':8192}}
    t=time.perf_counter()
    try:
        req=Request('http://127.0.0.1:11434/api/chat',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
        with urlopen(req,timeout=timeout) as r: d=json.loads(r.read().decode())
        return {'elapsed':time.perf_counter()-t,'response':d,'error':None,'request_summary':{'roles':[m['role'] for m in messages],'tool_call_counts':[len(m.get('tool_calls',[])) for m in messages],'tools_schema_hash':__import__('hashlib').sha256(json.dumps([TOOL],sort_keys=True).encode()).hexdigest(),'stream':False,'think':False,'num_ctx':8192}}
    except Exception as e: return {'elapsed':time.perf_counter()-t,'response':None,'error':repr(e)}
def classify(x):
    if x['error']: return 'TIMEOUT' if 'timed out' in x['error'] else 'ERROR'
    m=(x['response'] or {}).get('message',{}); calls=m.get('tool_calls',[])
    if calls: return 'NATIVE_TOOL_CALL'
    c=m.get('content','')
    if '[TOOL_CALLS]' in c: return 'TEXT_TOOL_IMITATION'
    if c.strip().startswith('{') and 'path' in c: return 'TEXT_JSON_IMITATION'
    return 'PLAIN_TEXT'
def main():
    out={'prompt':PROMPT,'tool_schema':TOOL,'models':[]}
    for model in MODELS:
        show=api_show(model); direct=api(model,[{'role':'user','content':PROMPT}])
        dm=direct.get('response',{}).get('message',{}) if direct.get('response') else {}; cont=None
        if classify(direct)=='NATIVE_TOOL_CALL':
            call=dm['tool_calls'][0]; aid=call.get('id',''); name=call.get('function',{}).get('name','read_repo_text')
            hist=[{'role':'user','content':PROMPT},dm,{'role':'tool','tool_name':name,'content':'WORKER-OK'}]
            cont=api(model,hist)
        req=WorkerRequest(task_text=PROMPT); hs=OllamaToolSession(req,tools=(SPEC,),model=model,timeout_seconds=30,continuation_timeout_seconds=60)
        t=time.perf_counter(); step=hs.start(); hi={'elapsed':time.perf_counter()-t,'transport_ok':step.transport_ok,'content':step.output_text,'tool_requests':[{'id':x.call_id,'name':x.name,'arguments':dict(x.arguments)} for x in step.tool_requests],'error':step.error}
        hc=None
        if step.tool_requests:
            t=time.perf_counter(); s2=hs.continue_with_tool_result(ToolResult(call_id=step.tool_requests[0].call_id,ok=True,output='WORKER-OK',error=None)); hc={'elapsed':time.perf_counter()-t,'transport_ok':s2.transport_ok,'content':s2.output_text,'tool_requests':[{'id':x.call_id,'name':x.name,'arguments':dict(x.arguments)} for x in s2.tool_requests],'error':s2.error}
        out['models'].append({'model':model,'show':show,'direct_initial':{'classification':classify(direct),**direct},'direct_continuation':None if cont is None else {'classification':classify(cont),**cont},'harness_initial':hi,'harness_continuation':hc})
    Path(__file__).with_name('result.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
def api_show(model):
    try:
        req=Request('http://127.0.0.1:11434/api/show',data=json.dumps({'name':model}).encode(),headers={'Content-Type':'application/json'},method='POST')
        with urlopen(req,timeout=10) as r: d=json.loads(r.read().decode())
        return {'digest':d.get('digest'),'details':d.get('details'),'size':d.get('size'),'template':d.get('template'),'capabilities':d.get('capabilities'),'parameters':d.get('parameters')}
    except Exception as e: return {'error':repr(e)}
if __name__=='__main__': main()

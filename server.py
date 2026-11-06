"""Experimental local MCP stdio adapter; AI-assisted application prototype.

Only checks supplied numbers against three fixed illustrative specifications.
No evaluation of code, file access, network calls, wallet access or AI API calls.
MIT. Copyright 2026 Juan Pablo Pérez Vélez.
"""
import json
import math
import sys
from checks import SPECS, compare

VERSION = '2025-11-25'
SUPPORTED = {VERSION, '2025-06-18', '2025-03-26'}
TOOL = {
    'name': 'verify_case',
    'description': 'Compare a numeric result with one fixed illustrative scientific specification. Returns assumptions and a reference derivation. Passing is not general scientific validation.',
    'inputSchema': {'type':'object', 'properties': {
        'case_id': {'type':'string', 'enum':list(SPECS)},
        'candidate_output': {'type':'number'}},
        'required':['case_id','candidate_output'], 'additionalProperties':False},
    'annotations': {'readOnlyHint':True, 'destructiveHint':False,
                    'idempotentHint':True, 'openWorldHint':False}}

def verify(arguments):
    if not isinstance(arguments, dict) or set(arguments) != {'case_id','candidate_output'}:
        raise ValueError('Exactly case_id and candidate_output are required.')
    key, value = arguments['case_id'], arguments['candidate_output']
    if not isinstance(key, str) or key not in SPECS:
        raise ValueError('Unknown fixed case.')
    if type(value) not in (int, float) or abs(value) > 1e9 or not math.isfinite(value):
        raise ValueError('A finite numeric result with absolute value <= 1e9 is required.')
    spec = SPECS[key]
    return {'case_id':key, 'specification':{k:v for k,v in spec.items() if not callable(v)},
            'result':compare(spec, value),
            'provenance':'AI-assisted specification, code and tests; independent domain review not completed.',
            'scope':'Only this fixed example and its assumptions; not certification or arbitrary-code validation.'}

def reject_constant(value):
    raise ValueError('Nonstandard JSON numeric constant: ' + value)

class Session:
    def __init__(self):
        self.initialized = False
        self.ready = False

    def handle(self, msg):
        request_id = msg.get('id') if isinstance(msg, dict) else None
        def error(code, text):
            return {'jsonrpc':'2.0','id':request_id,'error':{'code':code,'message':text}}
        def result(payload):
            return {'jsonrpc':'2.0','id':request_id,'result':payload}
        if not isinstance(msg, dict) or msg.get('jsonrpc') != '2.0' or not isinstance(msg.get('method'), str):
            return error(-32600, 'Invalid request')
        method, params = msg['method'], msg.get('params', {})
        if not isinstance(params, dict):
            return error(-32602, 'Parameters must be an object') if 'id' in msg else None
        if 'id' not in msg:
            if method == 'notifications/initialized' and self.initialized:
                self.ready = True
            return None
        if method == 'ping':
            return result({})
        if method == 'initialize':
            if self.initialized:
                return error(-32600, 'Already initialized')
            self.initialized = True
            requested = params.get('protocolVersion')
            return result({'protocolVersion':requested if requested in SUPPORTED else VERSION,
                           'capabilities':{'tools':{}},
                           'serverInfo':{'name':'checkbridge-prototype','version':'0.1.0'}})
        if not self.ready:
            return error(-32000, 'Initialize and send notifications/initialized first')
        if method == 'tools/list':
            return result({'tools':[TOOL]})
        if method == 'tools/call':
            if params.get('name') != TOOL['name']:
                return error(-32602, 'Unknown tool')
            try:
                record = verify(params.get('arguments'))
            except ValueError as exc:
                return result({'content':[{'type':'text','text':str(exc)}],'isError':True})
            return result({'content':[{'type':'text','text':json.dumps(record, ensure_ascii=False, allow_nan=False)}],
                           'structuredContent':record,'isError':False})
        return error(-32601, 'Method not found')

def main():
    session = Session()
    for line in sys.stdin:
        try:
            if len(line) > 65536:
                raise ValueError('Message too large')
            msg = json.loads(line, parse_constant=reject_constant)
            reply = session.handle(msg)
        except (ValueError, TypeError, RecursionError):
            reply = {'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Invalid JSON or oversized message'}}
        if reply is not None:
            print(json.dumps(reply, ensure_ascii=False, allow_nan=False), flush=True)

if __name__ == '__main__':
    main()

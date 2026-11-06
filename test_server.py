import json
from pathlib import Path
import subprocess
import sys
import unittest
from server import Session, verify

class AdapterTests(unittest.TestCase):
    def test_transport_negotiation_and_scientific_failure(self):
        requests = [
            {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'test','version':'1'}}},
            {'jsonrpc':'2.0','method':'notifications/initialized'},
            {'jsonrpc':'2.0','id':2,'method':'tools/list'},
            {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'verify_case','arguments':{'case_id':'steady_mixer','candidate_output':0.125}}},
            {'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'verify_case','arguments':{'case_id':'steady_mixer','candidate_output':0.11}}}]
        p = subprocess.run([sys.executable, str(Path(__file__).with_name('server.py'))], input=''.join(json.dumps(x)+'\n' for x in requests), capture_output=True, text=True, check=True, timeout=10)
        out = [json.loads(x) for x in p.stdout.splitlines()]
        self.assertEqual([x['id'] for x in out], [1,2,3,4])
        self.assertEqual(out[0]['result']['protocolVersion'], '2025-11-25')
        self.assertEqual(out[1]['result']['tools'][0]['name'], 'verify_case')
        bad = out[2]['result']['structuredContent']
        self.assertFalse(bad['result']['passed'])
        self.assertTrue(bad['result']['checks']['within_inlet_bounds'])
        self.assertFalse(bad['result']['checks']['solute_mass_conserved'])
        self.assertIn('oracle_derivation', bad['specification'])
        self.assertTrue(out[3]['result']['structuredContent']['result']['passed'])
        self.assertEqual(p.stderr, '')

    def test_rejects_invalid_values_and_unexpected_fields(self):
        for v in [True, None, '0.25', float('inf'), float('nan'), 10**1000, 1e10]:
            with self.assertRaises(ValueError): verify({'case_id':'concentration_units','candidate_output':v})
        with self.assertRaises(ValueError): verify({'case_id':'concentration_units','candidate_output':0.25,'code':'print(1)'})

    def test_no_tools_before_initialized_notification(self):
        s = Session()
        self.assertIn('error',s.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'}))
        s.handle({'jsonrpc':'2.0','id':2,'method':'initialize','params':{}})
        self.assertIn('error',s.handle({'jsonrpc':'2.0','id':3,'method':'tools/list'}))

    def test_unknown_case_and_unknown_tool_are_rejected(self):
        with self.assertRaises(ValueError): verify({'case_id':'arbitrary','candidate_output':1})
        s = Session();s.initialized=s.ready=True
        self.assertEqual(s.handle({'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'exec'}})['error']['code'],-32602)

    def test_invalid_json_does_not_break_next_request(self):
        p=subprocess.run([sys.executable,str(Path(__file__).with_name('server.py'))],input='bad json\n'+json.dumps({'jsonrpc':'2.0','id':7,'method':'ping'})+'\n',capture_output=True,text=True,check=True,timeout=10)
        out=[json.loads(x) for x in p.stdout.splitlines()]
        self.assertEqual(out[0]['error']['code'],-32700)
        self.assertEqual(out[1],{'jsonrpc':'2.0','id':7,'result':{}})

    def test_version_negotiation_has_explicit_fallback(self):
        r=Session().handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'unknown'}})
        self.assertEqual(r['result']['protocolVersion'],'2025-11-25')

if __name__ == '__main__': unittest.main()

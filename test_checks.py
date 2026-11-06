import math
import unittest
from checks import SPECS, compare, report


class WorkflowTests(unittest.TestCase):
    def test_reference_candidates_pass_all_checks(self):
        result=report();self.assertEqual(len(result['cases']),3)
        self.assertTrue(result['all_passed'])

    def test_known_unit_and_balance_faults_are_detected(self):
        result=report(True)
        self.assertFalse(result['all_passed'])
        self.assertTrue(all(not x['checks']['analytic_reference_match'] for x in result['cases']))
        mixer=next(x for x in result['cases'] if x['case_id']=='steady_mixer')
        self.assertFalse(mixer['checks']['solute_mass_conserved'])
        self.assertTrue(mixer['checks']['within_inlet_bounds'])

    def test_physical_bounds_alone_do_not_validate_units(self):
        decay=next(x for x in report(True)['cases'] if x['case_id']=='first_order_decay')
        self.assertTrue(decay['checks']['physical_bounds'])
        self.assertFalse(decay['checks']['analytic_reference_match'])

    def test_nonfinite_or_nonnumeric_values_are_rejected(self):
        for v in [float('nan'),float('inf'),None,'0.25',True]:
            self.assertFalse(compare(SPECS['concentration_units'],v)['passed'])

    def test_outside_tolerance_is_rejected(self):
        spec=SPECS['concentration_units']
        self.assertFalse(compare(spec,spec['reference']+1e-7)['passed'])


if __name__=='__main__':unittest.main()

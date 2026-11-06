"""Independent Checks: illustrative scientific-code verification workflow.

Initial AI-assisted application prototype, 2026-11-06. Standard library only.
The analytic specifications are separate from candidate implementations, but
both were drafted with AI assistance. This is not independent expert review.
MIT License. Copyright 2026 Juan Pablo Pérez Vélez.
"""
import argparse
import json
import math


SPECS = {
    'concentration_units': {
        'question': 'Convert 250 mg/L to kg/m^3.',
        'inputs': {'concentration_mg_per_litre': 250.0},
        'assumptions': ['Mass concentration; no chemical conversion or density assumption.'],
        'oracle_derivation': '1 mg = 1e-6 kg; 1 litre = 1e-3 m^3; ratio is 1e-3.',
        'reference': 0.25, 'unit': 'kg/m^3', 'tolerance_absolute': 1e-12,
        'candidate': lambda: 250.0 * 1e-6 / 1e-3,
        'deliberate_fault': lambda: 250.0 * 1e-6,
        'fault_description': 'Mass converted but litre-to-cubic-metre conversion omitted.'},
    'steady_mixer': {
        'question': 'Find outlet solute mass fraction for two steady inlet streams.',
        'inputs': {'stream_a_kg_per_s': 2.0, 'stream_a_mass_fraction': 0.2,
                   'stream_b_kg_per_s': 3.0, 'stream_b_mass_fraction': 0.05},
        'assumptions': ['Steady state.', 'No reaction, leakage, phase loss or accumulation.',
                        'Fractions and flows are mass based; outlet is well mixed.'],
        'oracle_derivation': 'Total flow=5 kg/s; solute flow=2*0.2+3*0.05=0.55 kg/s; fraction=0.55/5.',
        'reference': 0.11, 'unit': 'kg/kg', 'tolerance_absolute': 1e-12,
        'candidate': lambda: (2.0 * 0.2 + 3.0 * 0.05) / (2.0 + 3.0),
        'deliberate_fault': lambda: (0.2 + 0.05) / 2.0,
        'fault_description': 'Unweighted average replaces flow-weighted mass balance.'},
    'first_order_decay': {
        'question': 'Evaluate x after 300 s with x0=5 and k=0.2 per minute.',
        'inputs': {'x0': 5.0, 'k_per_minute': 0.2, 'time_seconds': 300.0},
        'assumptions': ['dx/dt=-k*x.', 'Constant nonnegative k.', 'Closed ideal first-order model.'],
        'oracle_derivation': 'Separating dx/x=-k dt gives x=x0*exp(-k*t); 300 s=5 min, so x=5/e.',
        'reference': 5.0 / math.e, 'unit': 'same as x0', 'tolerance_absolute': 1e-12,
        'candidate': lambda: 5.0 * math.exp(-(0.2 / 60.0) * 300.0),
        'deliberate_fault': lambda: 5.0 * math.exp(-0.2 * 300.0),
        'fault_description': 'Per-minute rate used with time in seconds without conversion.'}
}


def compare(spec, value):
    finite = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    error = abs(value - spec['reference']) if finite else None
    checks = {'finite_numeric_output': finite,
              'analytic_reference_match': finite and error <= spec['tolerance_absolute']}
    if spec is SPECS['steady_mixer']:
        checks['solute_mass_conserved'] = finite and abs(value * 5.0 - 0.55) <= 1e-12
        checks['within_inlet_bounds'] = finite and 0.05 <= value <= 0.2
    if spec is SPECS['first_order_decay']:
        checks['physical_bounds'] = finite and 0 <= value <= 5.0
    return {'candidate_output': value if finite else str(value),
            'absolute_error': error, 'checks': checks, 'passed': all(checks.values())}


def report(faults=False):
    cases=[]
    for key,spec in SPECS.items():
        case={k:v for k,v in spec.items() if not callable(v)}
        value=spec['deliberate_fault' if faults else 'candidate']()
        case.update(case_id=key,implementation_kind='deliberately_faulty_example' if faults else 'reference_candidate',**compare(spec,value))
        cases.append(case)
    return {'prototype': 'Independent Checks', 'version': '0.1-application',
            'provenance': 'AI-assisted specifications, code and tests; no independent expert audit yet.',
            'scope': 'Three illustrative mathematical models; no empirical or general correctness claim.',
            'all_passed': all(x['passed'] for x in cases), 'cases': cases}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--deliberate-faults',action='store_true')
    args=p.parse_args()
    result=report(args.deliberate_faults)
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    raise SystemExit(0 if result['all_passed'] else 1)


if __name__=='__main__':main()

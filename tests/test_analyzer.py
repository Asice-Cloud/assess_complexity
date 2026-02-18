import os
from assess_complexity import analyze_file


def test_sample_analysis_exists():
    here = os.path.dirname(__file__)
    sample = os.path.join(here, '..', 'examples', 'sample.c')
    sample = os.path.normpath(sample)
    res = analyze_file(sample)
    # basic expectations
    assert 'sum' in res
    assert 'nested' in res
    assert 'fib' in res


def test_complexity_values():
    here = os.path.dirname(__file__)
    sample = os.path.join(here, '..', 'examples', 'sample.c')
    sample = os.path.normpath(sample)
    res = analyze_file(sample)
    assert 'O(n' in res['sum']['complexity']
    assert 'O(n^2' in res['nested']['complexity'] or 'n^2' in res['nested']['complexity']
    assert '2^n' in res['fib']['complexity']

import pytest
from hyperon import ExpressionAtom

def test_with_str(runner):
    output = runner.run_query('!(match &space (, (gene $n1) ) (, (gene $n1)))')
    assert type(output) is list
    assert type(output[0][0]) is ExpressionAtom

def test_with_str(runner, meta_run):
    with pytest.raises(TypeError):
        runner.run_query(meta_run)

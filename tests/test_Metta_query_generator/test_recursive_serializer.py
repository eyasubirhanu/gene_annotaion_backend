import pytest
from hyperon import S, E, V

def test_string(runner):
    output = runner.recurssive_seralize("", [])
    assert output == []

def test_dict(runner):
    output = runner.recurssive_seralize({}, [])
    assert output == []

def test_list(runner):
    output = runner.recurssive_seralize([], [])
    assert output == []

def test_tuple(runner):
    output = runner.recurssive_seralize(tuple(), [])
    assert output == []

def test_set(runner):
    output = runner.recurssive_seralize(set(), [])
    assert output == []

def test_symbolatom_set(runner):
    with pytest.raises(TypeError):
        runner.recurssive_seralize(set([S("gene")]), [])
    

def test_variableatom(runner):
    with pytest.raises(AttributeError):
        runner.recurssive_seralize([V("gene")], [])

def test_expressionatom_variableatom(runner):
    with pytest.raises(AttributeError):
        runner.recurssive_seralize([E(V('gene'), V("ENSG00000175793"))], [])

def test_symbolatom(runner):
    out_list = []
    output = runner.recurssive_seralize([S("gene")], out_list)
    assert type(output) is list
    assert output is out_list
    assert output == ['gene']

def test_symbolatom_tuple(runner):
    out_list = []
    output = runner.recurssive_seralize(tuple([S("gene")]), out_list)
    assert type(output) is list
    assert output is out_list
    assert output == ['gene']

def test_expressionatom_empty(runner):
    out_list = []
    output = runner.recurssive_seralize([E()], out_list)
    assert type(output) is list
    assert output is out_list
    assert output == []

def test_non_empty_outlist(runner):
    out_list = ['gene']
    output = runner.recurssive_seralize([E()], out_list)
    assert type(output) is list
    assert output is out_list
    assert output == ['gene']

def test_expressionatom_syomolicatom(runner):
    out_list = []
    output = runner.recurssive_seralize([E(S('gene'), S("ENSG00000175793"))], out_list)
    assert type(output) is list
    assert output is out_list
    assert output == ['gene', "ENSG00000175793"]

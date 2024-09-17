import pytest
from hyperon import S, E, V

def test_symbolatom(runner):
    with pytest.raises(TypeError):
        runner.metta_seralizer(S("gene"))

def test_variableatom(runner):
    with pytest.raises(TypeError):
        runner.metta_seralizer(V("gene"))

def test_expresionatom(runner):
    with pytest.raises(TypeError):
        runner.metta_seralizer(E(S("gene"), S("ENSG00000175793")))

def test_symbollist(runner):
    with pytest.raises(AttributeError):
        runner.metta_seralizer([S("gene")])
    
def test_variablelist(runner):
    with pytest.raises(AttributeError):
        runner.metta_seralizer([V("gene")])    

def test_faulty_expresionatom_list(runner):
    test_list = [E(S(","), S("gene"), S("ENSG00000175793"))]
    output = runner.metta_seralizer(test_list)
    assert type(output) is list
    assert output == []

def test_odd_expressionatom_tuple(runner):
    test_tuple = tuple([E(E(S(","), S("gene"), S("ENSG00000175793")))])
    output = runner.metta_seralizer(test_tuple)
    assert type(output) is list
    assert type(output[0]) is tuple
    assert len(test_tuple) == len(output)
    assert output == [(',', 'gene', 'ENSG00000175793')]

def test_odd_expressionatom_list(runner):
    test_list = [E(E(S(","), S("gene"), S("ENSG00000175793")))]
    output = runner.metta_seralizer(test_list)
    assert type(output) is list
    assert type(output[0]) is tuple
    assert len(test_list) == len(output)
    assert output == [(',', 'gene', 'ENSG00000175793')]

def test_expressionatom_list(runner):
    test_list = [E(S(","), E(S("gene"), S("ENSG00000175793")))]
    output = runner.metta_seralizer(test_list)
    assert type(output) is list
    assert type(output[0]) is tuple
    assert len(test_list) == len(output)
    assert output == [('gene', 'ENSG00000175793')]

def test_large_exprssionatom_list(runner):
    # testing [(, (translates_to (transcript ENST00000307630) (protein P61981)))]
    test_list = [
        E(S(","), 
           E(S("translates_to"), 
             E(S("transcript"), S("ENST00000307630")), E(S("protein"), S("P61981"))))]
    output = runner.metta_seralizer(test_list)
    assert type(output) is list
    assert type(output[0]) is tuple
    assert len(test_list) == len(output)
    assert output == [('translates_to', 'transcript', 'ENST00000307630', 'protein', 'P61981')]

def test_multiple_expressionatom_list(runner):
    # testing [(, (translates_to (transcript ENST00000307630) (protein P61981))), (, (translates_to (transcript ENST00000627231) (protein P62258)))]
    test_list = [
        E(S(","), 
           E(S("translates_to"), 
             E(S("transcript"), S("ENST00000307630")), E(S("protein"), S("P61981")))),
        E(S(","), 
           E(S("translates_to"), 
             E(S("transcript"), S("ENST00000627231")), E(S("protein"), S("P62258"))))
    ]
    output = runner.metta_seralizer(test_list)
    assert type(output) is list
    assert type(output[0]) is tuple
    assert len(test_list) == len(output)
    assert output == [('translates_to', 'transcript', 'ENST00000307630', 'protein', 'P61981'), ('translates_to', 'transcript', 'ENST00000627231', 'protein', 'P62258')]

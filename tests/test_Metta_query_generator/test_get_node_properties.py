from tests.utils.parse_node import parse_node

def test_normal_input(runner, schema):
    test = [{
                'predicate': 'transcribed_to', 
                'source': 'gene ENSG00000101349', 
                'target': 'transcript ENST00000353224'
        }]
    output = runner.get_node_properties(test, schema)
    te = parse_node(output, schema)
    assert te == True

def test_single_node(runner, schema):
    test = [{'source': 'gene ENSG00000101349'}]
    output = runner.get_node_properties(test, schema)
    te = parse_node(output, schema)
    assert te == True


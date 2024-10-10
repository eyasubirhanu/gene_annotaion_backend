from app.lib.validator import validate_request

# def test_one_node_query(runner, schema, one_query_list):
    # query = one_query_list['node']
    # node_map = validate_request(query, schema)
    # query = runner.query_Generator(query, node_map)
    # expected_output = one_query_list['expected_output']
    # assert type(query) is list
    # assert query == expected_output

def test_multiple_node_query(runner, schema, multiple_query_list):
    query = multiple_query_list['node']
    node_map = validate_request(query, schema)
    query = runner.query_Generator(query, node_map)
    expected_output = multiple_query_list['expected_output']
    assert type(query) is list
    assert query[0] in expected_output
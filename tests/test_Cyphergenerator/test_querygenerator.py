from app.lib.validator import validate_request

def test_normal_query(runner, schema, query_list):
    query = query_list['node']
    node_map = validate_request(query, schema)
    query = runner.query_Generator(query, node_map)
    expected_output = query_list['expected_output']
    assert type(query) is list
    assert expected_output == query
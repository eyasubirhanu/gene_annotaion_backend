import pytest
from app.lib.validator import validate_request
# This test case runs a set of tests to verify the MeTTa_Query_Generator.queryGenerator()
# creates the expected query string to run against a metta object

# tests for missing key error
def test_input(runner):
    with pytest.raises(KeyError):
        runner.query_Generator({}, {})

def test_mulitple_fixtures(query_list, schema, runner):  
        query = query_list['node']
        node_map = validate_request(query, schema)
        query = runner.query_Generator(query, node_map)
        expected_output = query_list['expected_output']
        assert type(query) is str
        assert expected_output == query
    
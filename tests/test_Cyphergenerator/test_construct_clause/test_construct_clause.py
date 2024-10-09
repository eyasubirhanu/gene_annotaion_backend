def test_normal_node(runner, node_list):
    match_clause = node_list['match_clause']
    return_clause = node_list['return_clause']
    match = runner.construct_clause(match_clause, return_clause)
    assert isinstance(match, str)
    assert match == node_list['expected_output']
def test_normal_node(runner, node_list):
    match_no_preds, match_preds, return_no_preds, return_preds, expected_output = node_list.values()
    match = runner.construct_union_clause(match_preds, return_preds, match_no_preds, return_no_preds)
    assert isinstance(match, str)
    assert match == expected_output

import pytest

def test_listof_nodes(runner):
    node = []
    var_name = ''
    with pytest.raises(TypeError):
        runner.match_node(node, var_name)

def test_str_nodes(runner):
    node = ''
    var_name = ''
    with pytest.raises(TypeError):
        runner.match_node(node, var_name)

def test_set_nodes(runner):
    node = set()
    var_name = ''
    with pytest.raises(TypeError):
        runner.match_node(node, var_name)

def test_tuple_nodes(runner):
    node = tuple()
    var_name = ''
    with pytest.raises(TypeError):
        runner.match_node(node, var_name)


def test_normal_node(runner, node_list):
    node = node_list['node']
    var_name = node_list['var_name']
    match = runner.match_node(node, var_name)
    assert isinstance(match, str)
    assert match == node_list['expected_output']
from unittest.mock import MagicMock
from neo4j.graph import Node
from tests.utils.mocknode import create_testinput, create_testNode, create_testrelationship

def test_empty_string (runner, test_list):
    test = runner.process_result(test_list['query'], True)
    assert  isinstance(test, tuple)
    assert  isinstance(test[0], list)
    assert  isinstance(test[1], list)
    assert  isinstance(test[2], dict)
    assert  isinstance(test[3], dict)
    assert test == test_list['expected_output']


def test_node(runner, test_nodes):
    nodes = []
    for node in test_nodes['nodes']:
        nodes.append(create_testNode(node['id'], node['type'], node['properties']))

    test_input = create_testinput(nodes)
    test = runner.process_result(test_input, True)
    assert  isinstance(test, tuple)
    assert  isinstance(test[0], list)
    assert  isinstance(test[1], list)
    assert  isinstance(test[2], dict)
    assert  isinstance(test[3], dict)
    assert test == test_nodes['expected_output']

def test_edge(runner, test_edges):
    
    edges = []
    for edge in test_edges['edges']:
        edges.append(create_testrelationship(edge['type'], edge['start_label'], edge['start_id'], edge['end_label'], edge['end_id'], edge['properties']))

    test_input = create_testinput(edges)
    test = runner.process_result(test_input, True)
    assert  isinstance(test, tuple)
    assert  isinstance(test[0], list)
    assert  isinstance(test[1], list)
    assert  isinstance(test[2], dict)
    assert  isinstance(test[3], dict)
    assert test == test_edges['expected_output']

def test_node_edge(runner, test_nodes_edges):

    nodes = []
    edges = []

    for node in test_nodes_edges['nodes']:
        nodes.append(create_testNode(node['id'], node['type'], node['properties']))

    for edge in test_nodes_edges['edges']:
        edges.append(create_testrelationship(edge['type'], edge['start_label'], edge['start_id'], edge['end_label'], edge['end_id'], edge['properties']))

    test_input = create_testinput(nodes, edges)
    test = runner.process_result(test_input, True)
    assert  isinstance(test, tuple)
    assert  isinstance(test[0], list)
    assert  isinstance(test[1], list)
    assert  isinstance(test[2], dict)
    assert  isinstance(test[3], dict)
    assert test == test_nodes_edges['expected_output']
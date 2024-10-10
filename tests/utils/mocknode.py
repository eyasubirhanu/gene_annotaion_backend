from unittest.mock import MagicMock
import neo4j

def create_testNode(id, type, properties={}):
    test_node = MagicMock()
    test_node.__class__ = neo4j.graph.Node
    test_node.labels = [type]
    test_node.__getitem__.side_effect = lambda key: id if key == "id" else None
    test_node.items.return_value = properties.items()
    return(test_node)

def create_testrelationship(type, start_label, start_id, end_label, end_id, properties={}):
    test_relationship = MagicMock()
    test_relationship.__class__ = neo4j.graph.Relationship
    test_relationship.type = type
    test_relationship.start_node.labels = start_label
    test_relationship.start_node.__getitem__.side_effect = lambda key: start_id if key == "id" else None
    test_relationship.end_node.labels = end_label
    test_relationship.end_node.__getitem__.side_effect = lambda key: end_id if key == "id" else None
    test_relationship.items.return_value = properties.items()
    return test_relationship

def create_testinput(test_node=[], test_relationship=[]):
    result = {}
    for i in range(len(test_node)):
        result[f"n_{i}"] = test_node[i]
    
    for i in range(len(test_relationship)):
        result[f"r_{i}"] = test_relationship[i]

    return [result]
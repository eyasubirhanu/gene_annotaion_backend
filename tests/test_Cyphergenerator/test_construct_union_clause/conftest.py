import pytest

threenodes_onerelationship_nodeid = {
    'match_no_preds': ["(n_n3:gene {id: 'testcase'})"],
    'match_preds':['(n1:gene)', '(n1)-[r0:transcribed_to]->(n2:transcript)'],
    'return_no_preds': ['n_n3'],
    'return_pred': ['r0', 'n2', 'n1'],
    'expected_output': "MATCH (n1:gene), (n1)-[r0:transcribed_to]->(n2:transcript) RETURN r0, n2, n1 , null AS n_n3 UNION MATCH (n_n3:gene {id: 'testcase'}) RETURN  n_n3 , null AS r0, null AS n2, null AS n1"
}

threenodes_onerelationship_nodeid_nodeproperty = {
    'match_no_preds': ["(n_n3:gene {id: 'testcase', gene_type: 'protien_coding'})"],
    'match_preds':['(n1:gene)', '(n1)-[r0:transcribed_to]->(n2:transcript)'],
    'return_no_preds': ['n_n3'],
    'return_pred': ['r0', 'n2', 'n1'],
    'expected_output': "MATCH (n1:gene), (n1)-[r0:transcribed_to]->(n2:transcript) RETURN r0, n2, n1 , null AS n_n3 UNION MATCH (n_n3:gene {id: 'testcase', gene_type: 'protien_coding'}) RETURN  n_n3 , null AS r0, null AS n2, null AS n1"
}

threenodes_onerelationship_nodeid_relationproperty = {
    'match_no_preds': ["(n_n3:gene {id: 'testcase'})"],
    'match_preds':["(n1:gene)", "(n1)-[r0:transcribed_to {gene_type: 'protien_coding'}]->(n2:transcript)"],
    'return_no_preds': ['n_n3'],
    'return_pred': ['r0', 'n2', 'n1'],
    'expected_output': "MATCH (n1:gene), (n1)-[r0:transcribed_to {gene_type: 'protien_coding'}]->(n2:transcript) RETURN r0, n2, n1 , null AS n_n3 UNION MATCH (n_n3:gene {id: 'testcase'}) RETURN  n_n3 , null AS r0, null AS n2, null AS n1"
}

empty_list = {
    'match_no_preds': [],
    'match_preds':[],
    'return_no_preds': [],
    'return_pred': [],
    'expected_output': "MATCH  RETURN  , null AS  UNION MATCH  RETURN   , null AS "
}

empty_set = {
    'match_no_preds': set(),
    'match_preds':[],
    'return_no_preds': [],
    'return_pred': [],
    'expected_output': "MATCH  RETURN  , null AS  UNION MATCH  RETURN   , null AS "
}

empty_tuple = {
    'match_no_preds': tuple(),
    'match_preds':[],
    'return_no_preds': [],
    'return_pred': [],
    'expected_output': "MATCH  RETURN  , null AS  UNION MATCH  RETURN   , null AS "
}

empty_dict = {
    'match_no_preds': {},
    'match_preds':[],
    'return_no_preds': [],
    'return_pred': [],
    'expected_output': "MATCH  RETURN  , null AS  UNION MATCH  RETURN   , null AS "
}

empty_str = {
    'match_no_preds': '',
    'match_preds':[],
    'return_no_preds': [],
    'return_pred': [],
    'expected_output': "MATCH  RETURN  , null AS  UNION MATCH  RETURN   , null AS "
}


@pytest.fixture(params=[
 threenodes_onerelationship_nodeid,
 threenodes_onerelationship_nodeid_nodeproperty,
 threenodes_onerelationship_nodeid_relationproperty,
 empty_list,
 empty_set,
 empty_tuple,
 empty_dict,
 empty_str
])
def node_list(request):
    return request.param
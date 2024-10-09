import pytest

one_node_noid_noproperty = {
    'match_clause': ['(n_n1:gene)'],
    "return_clause" : ['n_n1'],
    'expected_output': "MATCH (n_n1:gene) RETURN n_n1"
}

one_node_id_noproperty = {
    'match_clause': ['(n_n1:gene {id: "testcase"})'],
    "return_clause" : ['n_n1'],
    'expected_output': 'MATCH (n_n1:gene {id: "testcase"}) RETURN n_n1'
}

one_node_noid_property = {
    'match_clause': ['(n_n1:gene {gene_type: "protein_coding"})'],
    "return_clause" : ['n_n1'],
    'expected_output': 'MATCH (n_n1:gene {gene_type: "protein_coding"}) RETURN n_n1'
}

one_node_noid_properties = {
    'match_clause': ['(n_n1:gene {gene_type: "protein_coding", chr: "chr1"})'],
    "return_clause" : ['n_n1'],
    'expected_output': 'MATCH (n_n1:gene {gene_type: "protein_coding", chr: "chr1"}) RETURN n_n1'
}

two_node_noid_nopropoerty = {
    'match_clause': ['(n_n1:gene)', '(n_n2:gene)'],
    "return_clause" : ['n_n1', 'n_n2'],
    'expected_output': 'MATCH (n_n1:gene), (n_n2:gene) RETURN n_n1, n_n2'
}

two_node_id_nopropoerty = {
    'match_clause': ['(n_n1:gene {id: "testcase"})', '(n_n2:gene {id: "testcase"})'],
    "return_clause" : ['n_n1', 'n_n2'],
    'expected_output': 'MATCH (n_n1:gene {id: "testcase"}), (n_n2:gene {id: "testcase"}) RETURN n_n1, n_n2'
}

two_node_noid_propoerty = {
    'match_clause': ['(n_n1:gene {gene_type: "testcase"})', '(n_n2:gene {gene_type: "testcase"})'],
    "return_clause" : ['n_n1', 'n_n2'],
    'expected_output': 'MATCH (n_n1:gene {gene_type: "testcase"}), (n_n2:gene {gene_type: "testcase"}) RETURN n_n1, n_n2'
}


@pytest.fixture(params=[
 one_node_noid_noproperty,
 one_node_id_noproperty,
 one_node_noid_property,
 one_node_noid_properties,
 two_node_noid_nopropoerty,
 two_node_id_nopropoerty,
 two_node_noid_propoerty
])
def node_list(request):
    return request.param
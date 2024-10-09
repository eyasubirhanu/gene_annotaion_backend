import pytest

one_node_list_varname = {
    'node' : {'node_id': 'n1', 'id': '', 'type': 'gene', 'properties': {}},
    'var_name' : [],
    'expected_output': '([]:gene)'
}
one_node_dict_varname = {
    'node' : {'node_id': 'n1', 'id': '', 'type': 'gene', 'properties': {}},
    'var_name' : {},
    'expected_output': '({}:gene)'
}

one_node_tuple_varname = {
    'node' : {'node_id': 'n1', 'id': '', 'type': 'gene', 'properties': {}},
    'var_name' : tuple(),
    'expected_output': '(():gene)'
}

one_node_set_varname = {
    'node' : {'node_id': 'n1', 'id': '', 'type': 'gene', 'properties': {}},
    'var_name' : set(),
    'expected_output': '(set():gene)'
}

one_node_noid_noproperty = {
    'node': {'node_id': 'n1', 'id': '', 'type': 'gene', 'properties': {}},
    'var_name': 'n_n1',
    'expected_output': '(n_n1:gene)'
}

one_node_id_noproperty = {
    'node': {'node_id': 'n1', 'id': 'testcase', 'type': 'gene', 'properties': {}},
    'var_name': 'n_n1',
    'expected_output': "(n_n1:gene {id: 'testcase'})"
}

one_node_noid_property = {
    'node': {'node_id': 'n1', 'id': '', 'type': 'gene', 'properties': {'gene_type': 'protein_coding'}},
    'var_name': 'n_n1',
    'expected_output': "(n_n1:gene {gene_type: 'protein_coding'})"
}

one_node_id_property = {
    'node': {'node_id': 'n1', 'id': 'testcase', 'type': 'gene', 'properties': {'gene_type': 'protein_coding'}},
    'var_name': 'n_n1',
    'expected_output': "(n_n1:gene {id: 'testcase'})"
}


@pytest.fixture(params=[
 one_node_noid_noproperty,
 one_node_id_noproperty,
 one_node_noid_property,
 one_node_id_property,
 one_node_list_varname,
 one_node_dict_varname,
 one_node_tuple_varname,
 one_node_set_varname
])
def node_list(request):
    return request.param
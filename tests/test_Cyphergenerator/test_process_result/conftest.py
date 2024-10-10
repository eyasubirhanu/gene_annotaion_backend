import pytest

test_empty_string = {
    'query': '',
    'expected_output': ([], [], {}, {})
}

test_empty_list = {
    'query': [],
    'expected_output': ([], [], {}, {})
}
test_empty_dict = {
    'query': {},
    'expected_output': ([], [], {}, {})
}
test_empty_tuple = {
    'query': tuple(),
    'expected_output': ([], [], {}, {})
}
test_empty_set = {
    'query': set(),
    'expected_output': ([], [], {}, {})
}

@pytest.fixture(params=[
    test_empty_string,
    test_empty_dict,
    test_empty_set,
    test_empty_tuple,
    test_empty_list
])
def test_list(request):
    return request.param

test_node_stingId = {
    'nodes':[
        {
        'id': 'testid',
        'type': 'gene',
        'properties': {'name': 'testname'}
    }],
    'expected_output': ([{'data': {'id': 'gene testid', 'name': 'testname', 'type': 'gene'}}], [], {'gene': [{'data': {'id': 'gene testid', 'name': 'testname', 'type': 'gene'}}]}, {})
}

test_node_intId_synonym = {
    'nodes':[
        {
        'id': 10,
        'type': 'gene',
        'properties': {'synonyms': 'testname'}
    }],
    'expected_output': ([{'data': {'id': 'gene 10', 'type': 'gene'}}], [], {'gene': [{'data': {'id': 'gene 10', 'type': 'gene'}}]}, {})
}

test_two_nodes_sameid = {
    'nodes':[
        {
        'id': 10,
        'type': 'gene',
        'properties': {'name': 'testname'}
    },
        {
        'id': 10,
        'type': 'gene',
        'properties': {'name': 'testname'}
    }
    ],
    'expected_output': (
        [{'data': {'id': 'gene 10', 'type': 'gene', 'name': 'testname'}}],
        [], 
        {'gene': [{'data': {'id': 'gene 10', 'type': 'gene', 'name': 'testname'}}]},
        {})
}

test_two_nodes_sameid_different_type = {
    'nodes':[
        {
        'id': 10,
        'type': 'gene',
        'properties': {'name': 'testname'}
    },
        {
        'id': 10,
        'type': 'transcript',
        'properties': {'name': 'testname'}
    }
    ],
    'expected_output': (
        [{'data': {'id': 'gene 10', 'type': 'gene', 'name': 'testname'}}, {'data': {'id': 'transcript 10', 'type': 'transcript', 'name': 'testname'}}],
        [], 
        {'gene': [{'data': {'id': 'gene 10', 'type': 'gene', 'name': 'testname'}}], 'transcript': [{'data': {'id': 'transcript 10', 'type': 'transcript', 'name': 'testname'}}]},
        {})
}

test_two_nodes = {
    'nodes':[
        {
        'id': 10,
        'type': 'gene',
        'properties': {'name': 'testname'}
    },
        {
        'id': 'testid',
        'type': 'gene',
        'properties': {'name': 'testname'}
    }
    ],
    'expected_output': (
        [{'data': {'id': 'gene 10', 'type': 'gene', 'name': 'testname'}}, {'data': {'id': 'gene testid', 'type': 'gene', 'name': 'testname'}}], 
        [], 
        {'gene': [{'data': {'id': 'gene 10', 'type': 'gene', 'name': 'testname'}}, {'data': {'id': 'gene testid', 'type': 'gene', 'name': 'testname'}}]},
        {})
}

@pytest.fixture(params=[
    test_node_stingId,
    test_node_intId_synonym,
    test_two_nodes_sameid,
    test_two_nodes,
    test_two_nodes_sameid_different_type
])
def test_nodes(request):
    return request.param

test_one_edge = {
    "edges": [
        {
            "type": 'transcribed_to',
            'start_label': ['gene'],
            'start_id': 'geneId',
            'end_label': ['transcript'], 
            'end_id': 'transcriptId',
            'properties': {
                'name': 'testname'
            }
        }],
    "expected_output": ([],
                        [{'data': {'label': 'transcribed_to', 'source': 'gene geneId', 'target': 'transcript transcriptId', 'name': 'testname'}}],
                        {},
                        {'transcribed_to': [{'data': {'label': 'transcribed_to', 'source': 'gene geneId', 'target': 'transcript transcriptId', 'name': 'testname'}}]})
}

test_one_edge_intId = {
    "edges": [
        {
            "type": 'transcribed_to',
            'start_label': ['gene'],
            'start_id': 10,
            'end_label': ['transcript'], 
            'end_id': 11,
            'properties': {
                'name': 'testname'
            }
        }],
    "expected_output": ([],
                        [{'data': {'label': 'transcribed_to', 'source': 'gene 10', 'target': 'transcript 11', 'name': 'testname'}}],
                        {},
                        {'transcribed_to': [{'data': {'label': 'transcribed_to', 'source': 'gene 10', 'target': 'transcript 11', 'name': 'testname'}}]})
}

test_two_edges = {   
    "edges": [
        {
            "type": 'translates_to',
            'start_label': ['transcript'],
            'start_id': 'transcriptId',
            'end_label': ['protien'], 
            'end_id': 'protienId',
            'properties': {
                'name': 'testname'
            }
        },
        {
            "type": 'transcribed_to',
            'start_label': ['gene'],
            'start_id': 'geneId',
            'end_label': ['transcript'], 
            'end_id': 'transcriptId',
            'properties': {
                'name': 'testname'
            }
        }],
    "expected_output": ([],
                        [{'data': {'label': 'translates_to', 'source': 'transcript transcriptId', 'target': 'protien protienId', 'name': 'testname'}}, {'data': {'label': 'transcribed_to', 'source': 'gene geneId', 'target': 'transcript transcriptId', 'name': 'testname'}}],
                        {},
                        {'translates_to': [{'data': {'label': 'translates_to', 'source': 'transcript transcriptId', 'target': 'protien protienId', 'name': 'testname'}}], 'transcribed_to': [{'data': {'label': 'transcribed_to', 'source': 'gene geneId', 'target': 'transcript transcriptId', 'name': 'testname'}}]})
}

@pytest.fixture(params=[
    test_one_edge,
    test_one_edge_intId,
    test_two_edges
])
def test_edges(request):
    return request.param


test_one_node_edge = {
    'nodes':[
        {
        'id': 'geneIds',
        'type': 'gene',
        'properties': {'name': 'testname'}
    }],
    "edges": [
        {
            "type": 'transcribed_to',
            'start_label': ['gene'],
            'start_id': 'geneId',
            'end_label': ['transcript'], 
            'end_id': 'transcriptId',
            'properties': {
                'name': 'testname'
            }
        }],
    'expected_output': (
        [{'data': {'id': 'gene geneIds', 'type': 'gene', 'name': 'testname'}}],
        [{'data': {'label': 'transcribed_to', 'source': 'gene geneId', 'target': 'transcript transcriptId', 'name': 'testname'}}], 
        {'gene': [{'data': {'id': 'gene geneIds', 'type': 'gene', 'name': 'testname'}}]},
        {'transcribed_to': [{'data': {'label': 'transcribed_to', 'source': 'gene geneId', 'target': 'transcript transcriptId', 'name': 'testname'}}]})
}

test_two_node_edge = {
    'nodes':[
        {
        'id': 'geneIds',
        'type': 'gene',
        'properties': {'name': 'testname'}
        },
        {
        'id': 'proteinId',
        'type': 'Protien',
        'properties': {'name': 'testname'}
        }
    ],
    "edges": [
        {
            "type": 'transcribed_to',
            'start_label': ['gene'],
            'start_id': 'geneId',
            'end_label': ['transcript'], 
            'end_id': 'transcriptId',
            'properties': {
                'name': 'testname'
            }
        }],
    'expected_output': (
        [{'data': {'id': 'gene geneIds', 'type': 'gene', 'name': 'testname'}}, {'data': {'id': 'Protien proteinId', 'type': 'Protien', 'name': 'testname'}}],
        [{'data': {'label': 'transcribed_to', 'source': 'gene geneId', 'target': 'transcript transcriptId', 'name': 'testname'}}], 
        {'gene': [{'data': {'id': 'gene geneIds', 'type': 'gene', 'name': 'testname'}}], 'Protien': [{'data': {'id': 'Protien proteinId', 'type': 'Protien', 'name': 'testname'}}]},
        {'transcribed_to': [{'data': {'label': 'transcribed_to', 'source': 'gene geneId', 'target': 'transcript transcriptId', 'name': 'testname'}}]})
}

test_node_two_edge ={
    'nodes':[
        {
        'id': 'geneIds',
        'type': 'gene',
        'properties': {'name': 'testname'}
        },
    ],
    "edges": [
        {
            "type": 'translates_to',
            'start_label': ['transcript'],
            'start_id': 'transcriptId',
            'end_label': ['protien'], 
            'end_id': 'protienId',
            'properties': {
                'name': 'testname'
            }
        },
        {
            "type": 'transcribed_to',
            'start_label': ['gene'],
            'start_id': 'geneId',
            'end_label': ['transcript'], 
            'end_id': 'transcriptId',
            'properties': {
                'name': 'testname'
            }
        }
        ],
    'expected_output': (
        [{'data': {'id': 'gene geneIds', 'type': 'gene', 'name': 'testname'}}],
        [{'data': {'label': 'translates_to', 'source': 'transcript transcriptId', 'target': 'protien protienId', 'name': 'testname'}}, {'data': {'label': 'transcribed_to', 'source': 'gene geneId', 'target': 'transcript transcriptId', 'name': 'testname'}}],
        {'gene': [{'data': {'id': 'gene geneIds', 'type': 'gene', 'name': 'testname'}}]},
        {'translates_to': [{'data': {'label': 'translates_to', 'source': 'transcript transcriptId', 'target': 'protien protienId', 'name': 'testname'}}], 'transcribed_to': [{'data': {'label': 'transcribed_to', 'source': 'gene geneId', 'target': 'transcript transcriptId', 'name': 'testname'}}]})

}

test_two_node_two_edge = {
    'nodes':[
        {
        'id': 'geneIds',
        'type': 'gene',
        'properties': {'name': 'testname'}
        },
        {
        'id': 'proteinId',
        'type': 'Protien',
        'properties': {'name': 'testname'}
        }
    ],
    "edges": [
        {
            "type": 'translates_to',
            'start_label': ['transcript'],
            'start_id': 'transcriptId',
            'end_label': ['protien'], 
            'end_id': 'protienId',
            'properties': {
                'name': 'testname'
            }
        },
        {
            "type": 'transcribed_to',
            'start_label': ['gene'],
            'start_id': 'geneId',
            'end_label': ['transcript'], 
            'end_id': 'transcriptId',
            'properties': {
                'name': 'testname'
            }
        }
        ],
    'expected_output': (
        [{'data': {'id': 'gene geneIds', 'type': 'gene', 'name': 'testname'}}, {'data': {'id': 'Protien proteinId', 'type': 'Protien', 'name': 'testname'}}],
        [{'data': {'label': 'translates_to', 'source': 'transcript transcriptId', 'target': 'protien protienId', 'name': 'testname'}}, {'data': {'label': 'transcribed_to', 'source': 'gene geneId', 'target': 'transcript transcriptId', 'name': 'testname'}}],
        {'gene': [{'data': {'id': 'gene geneIds', 'type': 'gene', 'name': 'testname'}}], 'Protien': [{'data': {'id': 'Protien proteinId', 'type': 'Protien', 'name': 'testname'}}]},
        {'translates_to': [{'data': {'label': 'translates_to', 'source': 'transcript transcriptId', 'target': 'protien protienId', 'name': 'testname'}}], 'transcribed_to': [{'data': {'label': 'transcribed_to', 'source': 'gene geneId', 'target': 'transcript transcriptId', 'name': 'testname'}}]})

}

@pytest.fixture(params=[
    test_one_node_edge,
    test_two_node_edge,
    test_node_two_edge,
    test_two_node_two_edge
])
def test_nodes_edges(request):
    return request.param
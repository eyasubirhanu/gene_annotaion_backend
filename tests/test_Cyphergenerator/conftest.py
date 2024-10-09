import pytest
from unittest.mock import patch, MagicMock
from app.services.cypher_generator import CypherQueryGenerator


@pytest.fixture()
def runner():
  with patch('neo4j.GraphDatabase.driver') as mock_driver:
    runner = CypherQueryGenerator("./cypher_data")
    # Mock session
    mock_session = MagicMock()
    mock_driver.return_value.session.return_value = mock_session

    # Mock return
    mock_run = MagicMock()
    mock_run.return_value = ['test']
    mock_session.run = mock_run

  # Mock driver's session method to return the mock session
    mock_driver.return_value.session.return_value = mock_session
    yield mock_driver

#query with only one node and no predicate
query_withoutpredicate = {
        "node": {
            "nodes": [
                {
                    "node_id": "n1",
                    "id": "",
                    "type": "gene",
                    "properties": {} 
                }]
            },
        "expected_output": ['MATCH (n_n1:gene) RETURN n_n1']
         }

#query with only one node and a node id
query_one_node_noid = {
          "node": {
            "nodes": [{
                "node_id": "n1",
                "id": "",
                "type": "gene",
                "properties": {} 
              }],
		        "predicates": []
          },
          "expected_output": ['MATCH (n_n1:gene) RETURN n_n1']
        }

query_one_node_with_id = {
          "node": {
            "nodes": [{
                "node_id": "n1",
                "id": "testcase",
                "type": "gene",
                "properties": {} 
              }],
		        "predicates": []
          },
          "expected_output": "!(match &space (, (gene testcase) ) (, (gene testcase)))"
        }

query_one_node_with_id_properties = {
          "node": {
            "nodes": [{
                "node_id": "n1",
                "id": "testcase",
                "type": "gene",
                "properties": {
                  "gene_type": "protein_coding"
                }
              }],
		        "predicates": []
          },
          "expected_output": ["MATCH (n_n1:gene {id: 'testcase'}) RETURN n_n1"]
        }

query_one_node_noid_with_oneproperty = {
          "node": {
            "nodes": [{
                "node_id": "n1",
                "id": "",
                "type": "gene",
                "properties": {
                  "gene_type": "protein_coding"
                }
              }],
		        "predicates": []
          },
          "expected_output": ["MATCH (n_n1:gene {gene_type: 'protein_coding'}) RETURN n_n1"]
        }

query_one_node_noid_with_properties = {
          "node": {
            "nodes": [{
                "node_id": "n1",
                "id": "",
                "type": "gene",
                "properties": {
                  "gene_type": "protein_coding",
                  "chr": "chr1"
                }
              }],
		        "predicates": []
          },
          "expected_output": ["MATCH (n_n1:gene {gene_type: 'protein_coding', chr: 'chr1'}) RETURN n_n1"]
        }

query_two_node_noid_noproperties = {
          "node": {
            "nodes": [{
                "node_id": "n1",
                "id": "",
                "type": "gene",
                "properties": {}
                },
                {
                "node_id": "n2",
                "id": "",
                "type": "gene",
                "properties": { }
                }
              ],
		        "predicates": []
          },
          "expected_output":  ['MATCH (n_n1:gene), (n_n2:gene) RETURN n_n1, n_n2']
        }

query_two_node_noid_with_properties = {
          "node": {
            "nodes": [{
                "node_id": "n1",
                "id": "",
                "type": "gene",
                "properties": {
                  "gene_type": "protein_coding"
                  }
                },
                {
                "node_id": "n2",
                "id": "",
                "type": "gene",
                "properties": {
                  "chr": "chr1"
                  }
                }
              ],
		        "predicates": []
          },
          "expected_output": ["MATCH (n_n1:gene {gene_type: 'protein_coding'}), (n_n2:gene {chr: 'chr1'}) RETURN n_n1, n_n2"]
        }

query_two_node_id_with_properties = {
          "node": {
            "nodes": [{
                "node_id": "n1",
                "id": "testcase",
                "type": "gene",
                "properties": {
                  "gene_type": "protein_coding"
                  }
                },
                {
                "node_id": "n2",
                "id": "",
                "type": "gene",
                "properties": {
                  "chr": "chr1"
                  }
                }
              ],
		        "predicates": []
          },
          "expected_output": ["MATCH (n_n1:gene {id: 'testcase'}), (n_n2:gene {chr: 'chr1'}) RETURN n_n1, n_n2"]
        }

query_two_node_with_predicate = {
          "node": {
            "nodes": [{
                "node_id": "n1",
                "id": "testcase",
                "type": "gene",
                "properties": {
                  "gene_type": "protein_coding"
                  }
                },
                {
                "node_id": "n2",
                "id": "",
                "type": "transcript",
                "properties": {}
                }
              ],
		        "predicates": [{
              "type": "transcribed to",
              "source": "n1",
              "target": "n2"
              }]
          },
          "expected_output":  ["MATCH (n1:gene {id: 'testcase'}), (n1)-[r0:transcribed_to]->(n2:transcript) RETURN r0, n1, n2"]
        }

query_three_node_with_predicate = {
      "node": {
        "nodes": [
          {
            "node_id": "n1",
            "id": "",
            "type": "gene",
            "properties": {
              "gene_type": "protein_coding"
            }
          },
          {
            "node_id": "n2",
            "id": "",
            "type": "transcript",
            "properties": {}
          },
          {
            "node_id": "n3",
            "id": "",
            "type": "protein",
            "properties": {
              "protein_name": "ANKE1"
            }
          }
        ],
        "predicates": [
          {
            "type": "transcribed to",
            "source": "n1",
            "target": "n2"
          }
      ]
      },
    "expected_output": ["MATCH (n1:gene {gene_type: 'protein_coding'}), (n1)-[r0:transcribed_to]->(n2:transcript) RETURN r0, n1, n2 , null AS n_n3 UNION MATCH (n_n3:protein {protein_name: 'ANKE1'}) RETURN  n_n3 , null AS r0, null AS n1, null AS n2"]
    }

query_json = {
  "node": {
    "nodes": [
      {
        "node_id": "n1",
        "id": "",
        "type": "gene",
        "properties": {
          "gene_type": "protein_coding"
        }
      },
      {
        "node_id": "n2",
        "id": "",
        "type": "transcript",
        "properties": {}
      },
      {
	"node_id": "n3",
        "id": "",
        "type": "protein",
        "properties": {
          "protein_name": "ANKE1"
        }
      }
    ],
    "predicates": [
      {
        "type": "transcribed to",
        "source": "n1",
        "target": "n2"
      }
   ]
  },
  "expected_output": ["MATCH (n1:gene {gene_type: 'protein_coding'}), (n1)-[r0:transcribed_to]->(n2:transcript) RETURN r0, n1, n2 , null AS n_n3 UNION MATCH (n_n3:protein {protein_name: 'ANKE1'}) RETURN  n_n3 , null AS r0, null AS n1, null AS n2"]
}

@pytest.fixture(params=[
  query_json,
  query_three_node_with_predicate,
  query_two_node_with_predicate,
  query_two_node_id_with_properties,
  query_two_node_noid_with_properties,
  query_two_node_noid_noproperties,
  query_one_node_noid_with_properties,
  query_one_node_noid_with_oneproperty,
  query_one_node_with_id_properties,
  query_one_node_noid,
  query_withoutpredicate
])
def query_list(request):
    return request.param
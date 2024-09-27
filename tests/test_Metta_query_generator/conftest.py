import pytest
from app.services.metta_generator import MeTTa_Query_Generator

@pytest.fixture()
def runner():
  runner = MeTTa_Query_Generator("./Data")
  return runner

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
        "expected_output": "!(match &space (, (gene $n1)"
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
          "expected_output": "!(match &space (, (gene $n1) ) (, (gene $n1)))"
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
          "expected_output": "!(match &space (, (gene testcase) ) (, (gene testcase)))"
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
          "expected_output": "!(match &space (, (gene_type (gene $n1) protein_coding) ) (, (gene $n1)))"
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
          "expected_output": "!(match &space (, (gene_type (gene $n1) protein_coding) (chr (gene $n1) chr1) ) (, (gene $n1)))"
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
          "expected_output": "!(match &space (, (gene $n1) (gene $n2) ) (, (gene $n1) (gene $n2)))"
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
          "expected_output": "!(match &space (, (gene_type (gene $n1) protein_coding) (chr (gene $n2) chr1) ) (, (gene $n1) (gene $n2)))"
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
          "expected_output": "!(match &space (, (gene testcase) (chr (gene $n2) chr1) ) (, (gene testcase) (gene $n2)))"
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
          "expected_output": "!(match &space (, (transcribed_to (testcase) (transcript $n2)) ) (, (transcribed_to (testcase) (transcript $n2))))"
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
    "expected_output": "!(match &space (, (protein_name (protein $n3) ANKE1) (gene_type (gene $n1) protein_coding) (transcribed_to (gene $n1) (transcript $n2)) ) (, (protein $n3) (transcribed_to (gene $n1) (transcript $n2))))"
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
  "expected_output": "!(match &space (, (protein_name (protein $n3) ANKE1) (gene_type (gene $n1) protein_coding) (transcribed_to (gene $n1) (transcript $n2)) ) (, (protein $n3) (transcribed_to (gene $n1) (transcript $n2))))"
}

@pytest.fixture(params=[query_json,
     query_three_node_with_predicate,
     query_two_node_with_predicate,
     query_two_node_id_with_properties,
     query_two_node_noid_with_properties,
     query_two_node_noid_noproperties,
     query_one_node_noid_with_properties,
     query_one_node_noid_with_oneproperty,
     query_one_node_with_id_properties,
     query_one_node_with_id,
     query_withoutpredicate
])
def query_list(request):
    return request.param


@pytest.fixture(params=[
   list('!(match &space (, (gene $n1) ) (, (gene $n1)))'),
   tuple('!(match &space (, (gene $n1) ) (, (gene $n1)))'),
   set('!(match &space (, (gene $n1) ) (, (gene $n1)))'),
   {'query': '!(match &space (, (gene $n1) ) (, (gene $n1)))'}
])

def meta_run(request):
  return request.param
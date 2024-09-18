import pytest
from app.lib.validator import validate_request 
from app import schema_manager

# Sample schema for the provided test cases
SAMPLE_SCHEMA = schema_manager.schema

# Sample request for some tests
SAMPLE_REQUEST = {
    "nodes": [
        {
            "node_id": "n1",
            "id": "",
            "type": "gene",
            "properties": {
                "gene_type": "protein_coding",
                "start": 9537370,
                "end": 9839076
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
}

def test_validate_request_missing_nodes():
    """Test case where 'nodes' field is missing from the request."""
    request = {"predicates": []}
    schema = SAMPLE_SCHEMA

    with pytest.raises(ValueError, match="The 'nodes' field is missing in the request."):
        validate_request(request, schema)

def test_validate_request_nodes_not_list():
    """Test case where 'nodes' field is not a list."""
    request = {"nodes": {}, "predicates": []}
    schema = SAMPLE_SCHEMA

    with pytest.raises(ValueError, match="'nodes' should be a list."):
        validate_request(request, schema)

def test_validate_request_node_not_dict():
    """Test case where an item in 'nodes' is not a dictionary."""
    request = {"nodes": ["node1"], "predicates": []}
    schema = SAMPLE_SCHEMA

    with pytest.raises(ValueError, match="Each node must be a dictionary."):
        validate_request(request, schema)

def test_validate_request_node_missing_id():
    """Test case where a node is missing the 'id' field."""
    request = {
        "nodes": [{"type": "gene", "node_id": "n1", "properties": {}}],
        "predicates": []
    }
    schema = SAMPLE_SCHEMA

    with pytest.raises(ValueError, match="Each node requires an 'id' field."):
        validate_request(request, schema)

def test_validate_request_node_missing_type():
    """Test case where a node is missing the 'type' field."""
    request = {
        "nodes": [{"id": "1", "node_id": "n1", "properties": {}}],
        "predicates": []
    }
    schema = SAMPLE_SCHEMA

    with pytest.raises(ValueError, match="Each node requires a 'type' field."):
        validate_request(request, schema)

def test_validate_request_node_missing_node_id():
    """Test case where a node is missing the 'node_id' field."""
    request = {
        "nodes": [{"id": "1", "type": "gene", "properties": {}}],
        "predicates": []
    }
    schema = SAMPLE_SCHEMA

    with pytest.raises(ValueError, match="Each node requires a 'node_id' field."):
        validate_request(request, schema)

def test_validate_request_node_missing_properties():
    """Test case where a node is missing the 'properties' field."""
    request = {
        "nodes": [{"id": "1", "type": "gene", "node_id": "n1"}],
        "predicates": []
    }
    schema = SAMPLE_SCHEMA

    with pytest.raises(ValueError, match="Each node requires a 'properties' field."):
        validate_request(request, schema)

def test_validate_request_node_type_not_in_schema():
    """Test case where node type is not present in the schema."""
    request = {
        "nodes": [{"id": "1", "type": "unknown", "node_id": "n1", "properties": {}}],
        "predicates": []
    }
    schema = SAMPLE_SCHEMA

    with pytest.raises(ValueError, match="Node type 'unknown' not found in the schema."):
        validate_request(request, schema)

def test_validate_request_node_property_not_in_schema():
    """Test case where a node has properties not defined in the schema."""
    request = {
        "nodes": [{"id": "1", "type": "gene", "node_id": "n1", "properties": {"unknown_property": "value"}}],
        "predicates": []
    }
    schema = SAMPLE_SCHEMA

    with pytest.raises(ValueError, match="Property 'unknown_property' doesn't exist in the schema for node type 'gene'."):
        validate_request(request, schema)

def test_validate_request_predicates_not_list():
    """Test case where 'predicates' field is not a list."""
    request = {
        "nodes": [{"id": "1", "type": "gene", "node_id": "n1", "properties": {}}],
        "predicates": {}
    }
    schema = SAMPLE_SCHEMA

    with pytest.raises(ValueError, match="'predicates' should be a list."):
        validate_request(request, schema)

def test_validate_request_predicate_missing_type():
    """Test case where a predicate is missing the 'type' field."""
    request = {
        "nodes": [{"id": "1", "type": "gene", "node_id": "n1", "properties": {}}],
        "predicates": [{"source": "n1", "target": "n2"}]
    }
    schema = SAMPLE_SCHEMA

    with pytest.raises(ValueError, match="Each predicate requires a 'type' field."):
        validate_request(request, schema)

def test_validate_request_predicate_missing_source_or_target():
    """Test case where a predicate is missing 'source' or 'target' field."""
    request = {
        "nodes": [{"id": "1", "type": "gene", "node_id": "n1", "properties": {}}],
        "predicates": [{"type": "transcribed to", "target": "n2"}]  # Missing 'source'
    }
    schema = SAMPLE_SCHEMA

    with pytest.raises(ValueError, match="Each predicate requires a 'source' field."):
        validate_request(request, schema)

    request_with_missing_target = {
        "nodes": [{"id": "1", "type": "gene", "node_id": "n1", "properties": {}}],
        "predicates": [{"type": "transcribed to", "source": "n1"}]  # Missing 'target'
    }

    with pytest.raises(ValueError, match="Each predicate requires a 'target' field."):
        validate_request(request_with_missing_target, schema)

def test_validate_request_predicate_source_or_target_not_in_nodes():
    """Test case where a predicate's source or target does not exist in 'nodes'."""
    request = {
        "nodes": [{"id": "1", "type": "gene", "node_id": "n1", "properties": {}}],
        "predicates": [{"type": "transcribed to", "source": "n1", "target": "n3"}]  # 'n3' not in nodes
    }
    schema = SAMPLE_SCHEMA

    with pytest.raises(ValueError, match="Target node 'n3' does not exist in the 'nodes' object."):
        validate_request(request, schema)

    request_with_invalid_source = {
        "nodes": [{"id": "1", "type": "gene", "node_id": "n1", "properties": {}}],
        "predicates": [{"type": "transcribed to", "source": "n3", "target": "n2"}]  # 'n3' not in nodes
    }

    with pytest.raises(ValueError, match="Source node 'n3' does not exist in the 'nodes' object."):
        validate_request(request_with_invalid_source, schema)

def test_validate_request_predicate_type_mismatch():
    """Test case where predicate type source and target types do not match schema."""
    request = {
        "nodes": [
            {"id": "1", "type": "gene", "node_id": "n1", "properties": {}},
            {"id": "2", "type": "protein", "node_id": "n2", "properties": {}}
        ],
        "predicates": [{"type": "transcribed to", "source": "n1", "target": "n2"}]
    }
    schema = {
        "transcribed to": {"source": "gene", "target": "transcript"}
    }

    with pytest.raises(ValueError, match="Node type 'protein' not found in the schema."):
        validate_request(request, schema)

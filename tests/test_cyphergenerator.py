import pytest
from unittest.mock import patch
from app.services.cypher_generator import CypherQueryGenerator
from app import schema_manager

import neo4j
from neo4j import GraphDatabase
from neo4j.graph import Node, Relationship

@pytest.fixture(scope='function')
def setup_database(monkeypatch):
    # Mock environment variables for Neo4j credentials
    monkeypatch.setenv('NEO4J_URI', 'neo4j+s://5b7a6817.databases.neo4j.io')
    monkeypatch.setenv('NEO4J_USERNAME', 'neo4j')
    monkeypatch.setenv('NEO4J_PASSWORD', 'LLG6MXReqYDEB8qwA-1mSeQPrlggoBHTpWewUhWdC_Y')

    # Initialize CypherQueryGenerator with the test dataset path
    generator = CypherQueryGenerator("./testData")

    # Clear the database to ensure tests run in isolation
    def clear_database():
        with generator.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    # Clear the database before running tests
    clear_database()

    yield generator

    # Cleanup after tests
    generator.close()

# Test Case 1: Load and Query Dataset
def test_load_and_query_dataset(setup_database):
    generator = setup_database

    # Load the dataset
    generator.load_dataset("./testData")

    # Example query to test
    query = "MATCH (n) RETURN COUNT(n) AS count"
    result = generator.run_query(query)

    # Assert that the expected number of nodes is returned
    expected_count = 242  # Adjust based on your test data
    assert result[0]["count"] == expected_count

# Test Case 2: Test Initialization with Invalid Dataset Path
def test_initialization_with_invalid_path(monkeypatch):
    monkeypatch.setenv('NEO4J_URI', 'neo4j+s://5b7a6817.databases.neo4j.io')
    monkeypatch.setenv('NEO4J_USERNAME', 'neo4j')
    monkeypatch.setenv('NEO4J_PASSWORD', 'LLG6MXReqYDEB8qwA-1mSeQPrlggoBHTpWewUhWdC_Y')
    
    # Invalid dataset path should raise an error
    with pytest.raises(ValueError, match="Dataset path"):
        CypherQueryGenerator("./invalid_path")

# Test Case 3: Test Query Generation with Empty Requests
def test_query_generator_with_empty_requests(setup_database):
    generator = setup_database

    # Simulate an empty request
    empty_requests = {"nodes": [], "predicates": []}

    # Expect a ValueError to be raised for an empty request
    with pytest.raises(ValueError, match="Request must contain at least one node or predicate"):
        generator.query_Generator(empty_requests, schema_manager.schema)

# Test Case 4: Test Dataset Loading Failure
@patch('app.services.cypher_generator.CypherQueryGenerator.load_dataset', side_effect=Exception("Loading failed"))
def test_dataset_loading_failure(mock_load_dataset, setup_database):
    # Simulate a dataset loading failure
    with pytest.raises(Exception, match="Loading failed"):
        setup_database.load_dataset("./testData")


# Test Case 5: Test Query Generation with Valid Nodes and Predicates
def test_query_generator_with_valid_nodes_and_predicates(setup_database):
    generator = setup_database

    # Define valid nodes and predicates
    requests = {
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

    # Use the real schema for validation
    schema = schema_manager.schema

    # Generate the Cypher query
    queries = generator.query_Generator(requests, schema)

    # Expected Cypher query
    expected_query = (
    "MATCH (s0:gene {gene_type: 'protein_coding', start: '9537370', end: '9839076'}), "
    "(s0)-[r0:transcribed_to]->(t0:transcript) "
    "RETURN r0, s0, t0"
    )

    # Assert that the generated query matches the expected query
    assert queries[0] == expected_query


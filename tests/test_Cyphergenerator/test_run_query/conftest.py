import pytest
from unittest .mock import patch, MagicMock
from app.services.cypher_generator import CypherQueryGenerator

@pytest.fixture()
def runner():
  with patch('neo4j.GraphDatabase.driver') as mock_driver:
    # Mock session
    mock_session = MagicMock()
    mock_driver.return_value.session.return_value = mock_session

    # Mock return
    mock_run = MagicMock()
    mock_run.return_value = ['test']
    mock_session.run = mock_run

    # Mock driver's session method to return the mock session
    mock_driver.return_value.session.return_value = mock_session
    runner = CypherQueryGenerator("./cypher_data")
    return runner

query = {
    "query_code": ["MATCH (n_n2:gene {id : 'ensg00000101349'}) RETURN n_n2"],
    'expected_output': ['test']
}
@pytest.fixture(params=[
    query
])
def querycode_list(request):
    return request.param
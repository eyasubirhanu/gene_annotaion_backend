import pytest
from unittest.mock import patch, MagicMock
from app.services.cypher_generator import CypherQueryGenerator


@pytest.fixture()
def runner():
    runner = CypherQueryGenerator("./cypher_data")
    return runner
import pytest
from app import app

# intializes a test_clinet
@pytest.fixture
def client():
    return app.test_client()

# list of nodes
@pytest.fixture
def node_list():
    return ['gene', 'transcript', 'pathway', 'go','enhancer','super enhancer','promoter','regulatory region','snp','protien','non coding rna']

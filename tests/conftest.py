import pytest
from app import app
from app.services.schema_data import SchemaManager

# intializes a test_clinet
@pytest.fixture
def client():
    return app.test_client()

# list of nodes
@pytest.fixture
def node_list():
    return ['gene', 'transcript', 'pathway', 'go','enhancer','super enhancer','promoter','regulatory region','snp','protien','non coding rna']

# for using against the schema check
@pytest.fixture
def schema():
   schema_manager = SchemaManager(schema_config_path='./config/schema_config.yaml', biocypher_config_path='./config/biocypher_config.yaml')
   return schema_manager.schema

from flask import Flask
from app.services.schema_data import SchemaManager
from app.services.metta_generator import MeTTa_Query_Generator
from app.services.cypher_generator import Cypher_Query_Generator

app = Flask(__name__)

databases = {
    # "metta": MeTTa_Query_Generator("./dataset"),
    "neo4j": Cypher_Query_Generator(
        "./neo4j_dataset", 
        neo4j_uri="bolt://neo4j:7687", 
        neo4j_username='neo4j', 
        neo4j_password='natanasrat', 
        loads_dataset=True
        )
    # Add other database instances here
}

schema_manager = SchemaManager(schema_config_path='./config/schema_config.yaml', biocypher_config_path='./config/biocypher_config.yaml')
# from app.services.cypher_chatbot import Chatbot
# chatbot = Chatbot(neo4j_uri="bolt://127.0.0.1:7687", 
#         neo4j_username='neo4j', 
#         neo4j_password='natanasrat',)
# print(chatbot.run_user_input("How many proteins are there"))
# Import routes at the end to avoid circular imports
from app import routes

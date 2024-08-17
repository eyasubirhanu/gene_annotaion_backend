from flask import Flask
from app.services.schema_data import SchemaManager
from app.services.cypher_generator import CypherQueryGenerator
from app.services.metta_generator import MeTTa_Query_Generator
from langchain_groq import ChatGroq


app = Flask(__name__)

databases = {
    # "metta": MeTTa_Query_Generator("./dataset"),
    "cypher": CypherQueryGenerator("./cypher")
    
    # Add other database instances here
}


schema_manager = SchemaManager(schema_config_path='./config/schema_config.yaml', biocypher_config_path='./config/biocypher_config.yaml')
from app.services.cypher_chatbot import Chatbot


chatbots = {
    # set environment key GROQ_API_KEY first
    # 'groq': Chatbot(llm=ChatGroq(temperature=0.0))
}
# Import routes at the end to avoid circular imports
from app import routes

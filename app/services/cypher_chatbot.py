from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
import os
from app import databases, schema_manager
from langchain_core.prompts.prompt import PromptTemplate
import yaml
schema_from_yaml = yaml.dump(schema_manager.get_schema())
CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
        Instructions:
        Use only the provided relationship types and properties in the schema.
        Do not use any other relationship types or properties that are not provided.
        Schema:
        {schema}""" +f"""
        You can use the following schema as well, input_label is the relationship type:
        {schema_from_yaml}
""" + """
        Note: Do not include any explanations or apologies in your responses.
        Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
        Do not include any text except the generated Cypher statement.
        The question is:
        {question}"""
CYPHER_GENERATION_PROMPT = PromptTemplate(
            input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
        )
        

class Chatbot():
    def __init__(self, llm) -> None:
        self.graph = Neo4jGraph(
            url=os.getenv('NEO4J_URI'), 
            username=os.getenv('NEO4J_USERNAME'), 
            password=os.getenv('NEO4J_PASSWORD'),
            # schema = schema_manager.get_schema()
        )
        print("Schema from graph: ", self.graph.get_schema)
        self.llm = llm
        self.cypher_chain = self.instantiate_cypher_chain()
    def instantiate_cypher_chain(self):
        self.graph.refresh_schema()
        cypher_chain = GraphCypherQAChain.from_llm(
            cypher_llm = self.llm,
            qa_llm = self.llm, graph=self.graph, verbose=True,
            return_intermediate_steps=True,
            cypher_prompt=CYPHER_GENERATION_PROMPT
        )
        return cypher_chain
    def run_user_input(self, input: str):
        response = self.cypher_chain.invoke(input)
        chat_response = response['result']

        intermediate_steps = response['intermediate_steps']
        cypher_llm_response = intermediate_steps[0]
        cypher_query = cypher_llm_response['query']
        print("CYPHER CHATBOT QUERY: ", cypher_query)
        query_result = self.get_query_result_from_db([cypher_query])

        return [chat_response, query_result]
    def get_query_result_from_db(self, query: str):
        
        db_instance = databases['cypher']
        result = db_instance.run_query(query)
        print("Result from graph: ", result)
        parsed_result = db_instance.parse_and_serialize(result, schema_manager.schema)
        
        response_data = {
            "nodes": parsed_result[0],
            "edges": parsed_result[1]
        }
        return response_data

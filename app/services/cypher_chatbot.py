from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
import os, json
import neo4j, neo4j.graph
from neo4j import GraphDatabase

from app import databases, schema_manager
from langchain_core.prompts.prompt import PromptTemplate
import yaml
from app.services.annotation_graph import process_graph

schema_from_yaml = yaml.dump(schema_manager.schema)
# CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
#         Instructions:
#         Use only the provided relationship types and properties in the schema.
#         Do not use any other relationship types or properties that are not provided.
#         Schema:
#         {schema}""" +f"""
#         You can use the following schema as well, input_label is the relationship type:
#         {schema_from_yaml}
# """ + """
#         Note: Do not include any explanations or apologies in your responses.
#         Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
#         Do not include any text except the generated Cypher statement.
#         The question is:
#         {question}"""
CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
        Instructions:
        Use only the provided relationship types and properties in the schema.
        Do not use any other relationship types or properties that are not provided.
        Schema:
        {schema}
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
        self.driver = GraphDatabase.driver(
            os.getenv('NEO4J_URI'),
            auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
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
    def run_query(self, query_code):
        with self.driver.session() as session:
            results = session.run(query_code[0])
            result_list = [record for record in results]
            return result_list
    
    def parse_neo4j_results(self, results):
        nodes = []
        edges = []
        node_dict = {}

        for record in results:
            for item in record.values():
                if isinstance(item, neo4j.graph.Node):
                    node_id = f"{list(item.labels)[0]} {item['id']}"
                    if node_id not in node_dict:
                        node_data = {
                            "data": {
                                "id": node_id,
                                "type": list(item.labels)[0],
                                "location": "",
                                "definition": "",
                                "name": "",
                                "group": [""],
                                **item
                            },
                            "group":"nodes"
                        }
                        nodes.append(node_data)
                        node_dict[node_id] = node_data
                elif isinstance(item, neo4j.graph.Relationship):
                    source_id = f"{list(item.start_node.labels)[0]} {item.start_node['id']}"
                    target_id = f"{list(item.end_node.labels)[0]} {item.end_node['id']}"
                    item_dict = dict(item)  
    
                    # Pop 'source' and 'target' if they exist
                    item_dict.pop("source", None)
                    item_dict.pop("target", None)
                    edge_data = {
                        "data": {
                            "id": item.id,
                            "label": item.type,
                            "source": source_id,
                            "target": target_id,
                            "pubmedId": "",
                            "subgroup": "",
                            "name": "",
                            "group": [""],
                            **item_dict
                        },
                        "group":"edges"
                    }
                    edges.append(edge_data)

        return {"nodes": nodes, "edges": edges}

    def parse_and_serialize(self, input,schema):
        parsed_result = self.parse_neo4j_results(input)
        return parsed_result["nodes"], parsed_result["edges"]

           
    def get_node_data(self, node:neo4j.graph.Node):
        properties = node._properties.copy()
        node_id = properties.pop('id', '')
        label = list(node.labels)[0]
        data = {
                "id": f"{label} {node_id}",
                "label": label,
                "type": label,
                **properties
            }
        # data_short = {
        #         "id": f"{label} {node_id}",
        #         "label": label,
        #         "type": label
        #     }
        # self.logger.debug(str(data_short))
        return data
    def get_query_result_from_db(self, query: str):
        
        result = self.run_query(query)
        parsed_result = self.parse_and_serialize(result, schema_manager.schema)
        response_data = {
            "nodes": parsed_result[0],
            "edges": parsed_result[1]
        }

        annotation_graph_data = json.dumps(response_data)
        annotation_graph = process_graph(annotation_graph_data)
        return json.loads(annotation_graph)

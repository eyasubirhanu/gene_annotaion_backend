from .query_generator_interface import QueryGeneratorInterface
from neo4j import GraphDatabase
from app.lib import validate_request

class Cypher_Query_Generator(QueryGeneratorInterface):
    def __init__(self, dataset_path: str):
        uri = "neo4j+s://2838a353.databases.neo4j.io"
        user = "neo4j"
        password = "_xmUcjpnF0ZKDOVeRY6dSZ_tfFGLDvW8mDVF0eC1p6w" 
    
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.dataset_path = dataset_path
        #self.load_dataset(self.dataset_path)

    def load_dataset(self, path: str):
        with open(path, 'r') as file:
            queries = file.read().split(';')
        query_code = [query.strip() for query in queries if query.strip()]

        self.run_query(query_code)

    def query_Generator(self, data, schema):
        node_map = validate_request(data, schema)

        if node_map is None:
            raise Exception('error')

        nodes = data['nodes']
        match_statements = []
        return_statements = []

        node_without_predicate = None
        predicates = None
        if "predicates" not in data:
            node_without_predicate = nodes
        else:
            predicates = data['predicates']
            node_with_predicate = set()
            for predicate in predicates:
                node_with_predicate.add(predicate["source"])
                node_with_predicate.add(predicate["target"])
            node_without_predicate = [node for node in nodes if node["node_id"] not in node_with_predicate]
        
        if "predicates" not in data or (node_without_predicate is not None and len(node_without_predicate) != 0):
            for node in node_without_predicate:
                node_type = node["type"]
                node_properties_str = ", ".join([f"{k}: '{v}'" for k, v in node["properties"].items()])
                if node['id']:
                    match_statement = f"({node['node_id']}:{node_type} {{id: '{node['id']}'}})"
                else:
                    match_statement = f"({node['node_id']}:{node_type} {{{node_properties_str}}})"

                return_statements.append(node['node_id'])
                return_statements = list(set(return_statements))
                match_statements.append(match_statement)

        if predicates is None:
            match_query = "MATCH " + ", ".join(match_statements)
            return_query = "RETURN " + ", ".join(return_statements)
            cypher_output = f"{match_query} {return_query}"
            print("OUTPUT", cypher_output)
            return cypher_output

        for predicate in predicates:
            predicate_type = predicate['type'].replace(" ", "_")
            source_id = predicate['source']
            print("source_id", source_id)
            target_id = predicate['target']
            print("target_id", target_id)

            # get source node
            source_node = node_map[source_id]
            print("source_node", source_node)
            source_node_type = source_node["type"]
            source_node_properties_str = ", ".join([f"{k}: '{v}'" for k, v in source_node["properties"].items()])
            if source_node['id']:
                source_match = f"({source_node['node_id']}:{source_node_type} {{id: '{source_node['id']}'}})"
            else:
                source_match = f"({source_node['node_id']}:{source_node_type} {{{source_node_properties_str}}})"
            
            #get target node
            target_node = node_map[target_id]
            print("target_node", target_node)
            target_node_type = target_node["type"]
            target_node_properties_str = ", ".join([f"{k}: '{v}'" for k, v in target_node["properties"].items()])
            if target_node['id']:
                target_match = f"({target_node['node_id']}:{target_node_type} {{id: '{target_node['id']}'}})"
            else:
                target_match = f"({target_node['node_id']}:{target_node_type} {{{target_node_properties_str}}})"
            return_statements.append(source_node['node_id'])
            return_statements.append(target_node['node_id'])
            return_statements = list(set(return_statements))
            match_statement = f" {source_match}-[:{predicate_type}]-{target_match}"
            match_statements.append(match_statement)
        match_query = "MATCH " + ", ".join(match_statements)
        return_query = "RETURN " + ", ".join(return_statements)
        cypher_output = f"{match_query} {return_query}"
        return cypher_output
        
    def run_query(self, query_code):
        with self.driver.session(database="neo4j") as session:
            result = session.run(query_code)
            result = result.data()

        return result
    def parse_and_serialize(self, input, schema=None):
        result_nodes = []
        result_edge = []
        result = []
        for nodes in input:
            result_nodes.extend([{"data": node} for node in nodes.values()])
        
        # TODO do for the relationship
        result.append(result_nodes)
        result.append(result_edge)
        return result
        

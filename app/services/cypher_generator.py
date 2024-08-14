from .query_generator_interface import QueryGeneratorInterface
import json
import neo4j, neo4j.graph
from neo4j import GraphDatabase
import os, glob

class Cypher_Query_Generator(QueryGeneratorInterface):
    def __init__(self, dataset_path: str, neo4j_uri: str, neo4j_username: str, neo4j_password: str, loads_dataset: bool = True):
        self.authenticate(neo4j_uri=neo4j_uri, neo4j_username=neo4j_username, neo4j_password=neo4j_password)
        self.dataset_path = dataset_path
        if loads_dataset:
            self.load_dataset(self.dataset_path)
    def authenticate(self, neo4j_uri: str, neo4j_username: str, neo4j_password: str):
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))
        driver.verify_connectivity()
        self.driver = driver
        self.session = driver.session()
    def load_dataset(self, path: str) -> None:
        if not os.path.exists(path):
            raise ValueError(f"Dataset path '{path}' does not exist.")
        paths = glob.glob(os.path.join(path, "**/*.cypher"), recursive=True)
        
        if not paths:
            raise ValueError(f"No cypher files found in dataset path '{path}'.")
        node_paths = [p for p in paths if 'nodes.cypher' in p.lower()]
        edge_paths = [p for p in paths if 'edges.cypher' in p.lower()]
        all_paths = node_paths + edge_paths
        for path in all_paths:
            print(f"Start loading dataset from '{path}'...")
            try:
                with open(path, 'r') as file:
                    lines = file.readlines()

                for line in lines:
                    query = line.strip()
                    if query:
                        self.run_query(query)
            except Exception as e:
                print(f"Error loading dataset from '{path}': {e}")
        print(f"Finished loading {len(paths)} datasets.")

    def query_Generator(self, data):
        # This part was handled by validator
        nodes = {node['node_id']: node for node in data['nodes']}
        
        
        predicates = data['predicates']
        match_statements = []
        return_statements = []
        for node in data['nodes']:
            node_type = node["type"]
            node_properties_str = ", ".join([f"{k}: '{v}'" for k, v in node["properties"].items()])
            if node['id']:
                match_statement = f"({node['node_id']}:{node_type} {{id: '{node['id']}'}})"
            else:
                match_statement = f"({node['node_id']}:{node_type} {{{node_properties_str}}})"
            match_statements.append(match_statement)
            return_statements.append(node['node_id'])

        for predicate in predicates:
            predicate_type = predicate['type'].replace(" ", "_")
            source_id = predicate['source']
            target_id = predicate['target']

            predicate_generated_id =  source_id + "_" + predicate_type + "_" + target_id

            # get source node
            source_node = nodes[source_id]
            source_node_type = source_node["type"]
            source_node_properties_str = ", ".join([f"{k}: '{v}'" for k, v in source_node["properties"].items()])
            if source_node['id']:
                source_match = f"({source_node['node_id']}:{source_node_type} {{id: '{source_node['id']}'}})"
            else:
                source_match = f"({source_node['node_id']}:{source_node_type} {{{source_node_properties_str}}})"
            
            #get target node
            target_node = nodes[target_id]
            target_node_type = target_node["type"]
            target_node_properties_str = ", ".join([f"{k}: '{v}'" for k, v in target_node["properties"].items()])
            if target_node['id']:
                target_match = f"({target_node['node_id']}:{target_node_type} {{id: '{target_node['id']}'}})"
            else:
                target_match = f"({target_node['node_id']}:{target_node_type} {{{target_node_properties_str}}})"
            return_statements.append(source_node['node_id'])
            return_statements.append(target_node['node_id'])
            return_statements.append(predicate_generated_id)
            match_statement = f" {source_match}-[{predicate_generated_id}:{predicate_type}]->{target_match}"
            match_statements.append(match_statement)
        return_statements = list(set(return_statements))
        match_query = "MATCH " + ", ".join(match_statements)
        return_query = "RETURN " + ", ".join(return_statements)
        cypher_output = f"{match_query} {return_query}"
        return cypher_output

    def parse_and_serialize(self, input_response) -> str:
        values = input_response.values()
        nodes = []
        edges = []
        included_ids = []
        for record in values:
            items_map = {}
            for item in record:
                items_map[item.id] = item
            
            for item in record:
                if isinstance(item, neo4j.graph.Relationship):
                    predicate_properties = item._properties.copy()
                    predicate_id = predicate_properties.pop('id', '')
                    predicate_type = item.type
                    
                    source_id = item._start_node.id
                    source_node = items_map[source_id]
                    source_node_data = self.get_node_data(source_node)
                    if source_id not in included_ids:
                        nodes.append({"data": source_node_data})
                        included_ids.append(source_id)
                    
                    target_id = item._end_node.id
                    target_node = items_map[target_id]
                    target_node_data = self.get_node_data(target_node)
                    
                    if target_id not in included_ids:
                        nodes.append({"data": target_node_data})
                        included_ids.append(target_id)
                    predicate_properties.pop("source", None)
                    predicate_data = {
                        "id": f"{predicate_type} {predicate_id}",
                        "label": predicate_type,
                        "source_node": source_node_data['id'],
                        "target_node": target_node_data['id'],
                        **predicate_properties
                    }
                    p_d_short = {
                        "id": f"{predicate_type} {predicate_id}",
                        "label": predicate_type,
                        "source": source_node_data['id'],
                        "target": target_node_data['id']
                    }
                    edges.append({
                        "data": predicate_data
                    })
                    included_ids.append(predicate_id)
                    
                elif isinstance(item, neo4j.graph.Node):
                    if item.id not in included_ids:
                        node_data = self.get_node_data(item)
                        nodes.append(
                          {
                              "data": node_data
                          }
                          )
                        included_ids.append(item.id)
        parsed_data = {
            "nodes": nodes,
            "edges": edges
        }
        return json.dumps(parsed_data) 

           
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
        return data
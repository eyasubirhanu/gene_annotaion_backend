import glob
import os
from hyperon import MeTTa
import re
import json
import uuid
from .query_generator_interface import QueryGeneratorInterface
from app.lib import metta_seralizer
# from app.services.util import generate_id

class MeTTa_Query_Generator(QueryGeneratorInterface):
    def __init__(self, dataset_path: str):
        self.metta = MeTTa()
        self.initialize_space()
        self.dataset_path = dataset_path
        self.load_dataset(self.dataset_path)

    def initialize_space(self):
        self.metta.run("!(bind! &space (new-space))")

    def load_dataset(self, path: str) -> None:
        if not os.path.exists(path):
            raise ValueError(f"Dataset path '{path}' does not exist.")
        paths = glob.glob(os.path.join(path, "**/*.metta"), recursive=True)
        if not paths:
            raise ValueError(f"No .metta files found in dataset path '{path}'.")
        for path in paths:
            print(f"Start loading dataset from '{path}'...")
            try:
                self.metta.run(f'''
                    !(load-ascii &space {path})
                    ''')
            except Exception as e:
                print(f"Error loading dataset from '{path}': {e}")
        print(f"Finished loading {len(paths)} datasets.")

    def generate_id(self):
        import uuid
        return str(uuid.uuid4())[:8]

    def construct_node_representation(self, node, identifier):
        node_type = node['type']
        node_representation = ''
        for key, value in node['properties'].items():
            node_representation += f' ({key} ({node_type + " " + identifier}) {value})'
        return node_representation

    def query_Generator(self, data, schema):

        node_map = self.validate_request(data, schema)
        nodes = data['nodes']

        metta_output = '''!(match &space (,'''
        output = ''' (,'''

        print("node_map",node_map) 
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

        # if there is no predicate
        if "predicates" not in data or (node_without_predicate is not None and len(node_without_predicate) != 0):
            for node in node_without_predicate:
                node_type = node["type"]
                node_id = node["node_id"]
                node_identifier = '$' + node["node_id"]
                if node["id"]:
                    essemble_id = node["id"]
                    metta_output += f' ({node_type} {essemble_id})'
                    output += f' ({node_type} {essemble_id})'
                else:
                    if len(node["properties"]) == 0:
                        metta_output += f' ({node_type} ${node_id})'
                    else:
                        metta_output += self.construct_node_representation(node, node_identifier)
                    output += f' ({node_type} {node_identifier})'
        
        if predicates is None:
            return metta_output

        for predicate in predicates:
            predicate_type = predicate['type'].replace(" ", "_")
            source_id = predicate['source']
            print("source_id", source_id)
            target_id = predicate['target']
            print("target_id", target_id)

            # Handle source node
            source_node = node_map[source_id]
            print("source_node", source_node)
            if not source_node['id']:
                node_identifier = "$" + source_id
                metta_output += self.construct_node_representation(source_node, node_identifier)
                source = f'({source_node["type"]} {node_identifier})'
            else:
                source = f'({str(source_node["id"])})'

            # Handle target node
            target_node = node_map[target_id]
            if not target_node['id']:
                target_identifier = "$" + target_id
                metta_output += self.construct_node_representation(target_node, target_identifier)
                target = f'({target_node["type"]} {target_identifier})'
            else:
                target = f'({str(target_node["id"])})'

            # Add relationship
            metta_output += f' ({predicate_type} {source} {target})'
            output += f' ({predicate_type} {source} {target})'

        metta_output += f' ){output}))'
        print("metta_output:", metta_output)
        return metta_output


    def run_query(self, query_code):
        return self.metta.run(query_code)

    def parse_and_serialize(self, input):
        result = []

        tuples = metta_seralizer(input[0])
        for tuple in tuples:
            if len(tuple) == 2:
                src_type, src_id = tuple
                result.append({
                    "id": str(uuid.uuid4()),
                    "source": f"{src_type} {src_id}"
                })
            else:
                predicate, src_type, src_id, tgt_type, tgt_id = tuple
                result.append({
                "id": str(uuid.uuid4()),
                "predicate": predicate,
                "source": f"{src_type} {src_id}",
                "target": f"{tgt_type} {tgt_id}"
                })
        return result 

        
    # def parse_metta(self, input_string):
    #     parsed_metta = self.metta.parse_all(input_string)
    #     print("parsed_metta",parsed_metta)

    def parse_and_serialize_properties(self, input):
        nodes = {}
        relationships_dict = {}
        result = []
        tuples = metta_seralizer(input)
        print("result", tuples)

        for match in tuples:
            graph_attribute = match[0]
            match = match[1:]

            if graph_attribute == "node":
                if len(match) > 4:
                    predicate = match[0]
                    src_type = match[1]
                    src_value = match[2]
                    tgt = ' '.join(match[3:])
                else:
                    predicate, src_type, src_value, tgt = match
                if (src_type, src_value) not in nodes:
                    nodes[(src_type, src_value)] = {
                        "id": f"{src_type} {src_value}",
                        "type": src_type,
                    }
                nodes[(src_type, src_value)][predicate] = tgt
            elif graph_attribute == "edge":
                property_name, predicate, source, source_id, target, target_id = match[:6]
                value = ' '.join(match[6:])

                key = (predicate, source, source_id, target, target_id)
                if key not in relationships_dict:
                    relationships_dict[key] = {
                        "label": predicate,
                        "source_node": f"{source} {source_id}",
                        "target_node": f"{target} {target_id}",
                    }
                relationships_dict[key][property_name] = value

        node_list = [{"data": node} for node in nodes.values()]
        relationship_list = [{"data": relationship} for relationship in relationships_dict.values()]

        result.append(node_list)
        result.append(relationship_list)
        return result

    def get_node_properties(self, results, schema):
        metta = ('''!(match &space (,''')
        output = (''' (,''') 
        nodes = set()
        for result in results:
            source = result['source']
            source_node_type = result['source'].split(' ')[0]

            if source not in nodes:
                for property, _ in schema[source_node_type]['properties'].items():
                    id = self.generate_id()
                    metta += " " + f'({property} ({source}) ${id})'
                    output += " " + f'(node {property} ({source}) ${id})'
                nodes.add(source)

            if "target" in result and "predicate" in result:
                target = result['target']
                target_node_type = result['target'].split(' ')[0]
                if target not in nodes:
                    for property, _ in schema[target_node_type]['properties'].items():
                        id = self.generate_id()
                        metta += " " + f'({property} ({target}) ${id})'
                        output += " " + f'(node {property} ({target}) ${id})'
                    nodes.add(target)
        
                predicate = result['predicate']
                predicate_schema = ' '.join(predicate.split('_'))
                for property, _ in schema[predicate_schema]['properties'].items():
                    random = self.generate_id()
                    metta += " " + f'({property} ({predicate} ({source}) ({target})) ${random})'
                    output +=  " " + f'(edge {property} ({predicate} ({source}) ({target})) ${random})' 

        metta+= f" ) {output}))"

        return metta
    def validate_request(self, request, schema):
        if 'nodes' not in request:
            raise Exception("node is missing")

        nodes = request['nodes']
        
        # validate nodes
        if not isinstance(nodes, list):
            raise Exception("nodes should be a list")

        for node in nodes:
            if not isinstance(node, dict):
                raise Exception("Each node must be a dictionary")
            if 'id' not in node:
                raise Exception("id is required!")
            if 'type' not in node or node['type'] == "":
                raise Exception("type is required")
            if 'node_id' not in node or node['node_id'] == "":
                raise Exception("node_id is required")
            if 'properties' not in node:
                raise Exception("properties is required")
        
        # validate properties of nodes
        for node in nodes:
            properties = node['properties']
            node_type = node['type']
            for property in properties.keys():
                if property not in schema[node_type]['properties']:
                    raise Exception(f"{property} doesn't exsist in the schema!")

        node_map = {node['node_id']: node for node in nodes}
        # validate predicates
        if 'predicates' in request:
            predicates = request['predicates']
            
            if not isinstance(predicates, list):
                raise Exception("Predicate should be a list")
            for predicate in predicates:
                if 'type' not in predicate or predicate['type'] == "":
                    raise Exception("predicate type is required")
                if 'source' not in predicate or predicate['source'] == "":
                    raise Exception("source is required")
                if 'target' not in predicate or predicate['target'] == "":
                    raise Exception("target is required")
                
                predicate_schema = schema[predicate['type']]
                
                source_type = node_map[predicate['source']]['type']
                target_type = node_map[predicate['target']]['type']

                if predicate_schema['source'] != source_type or predicate_schema['target'] != target_type:
                    raise Exception(f"{predicate['type']} have source as {predicate_schema['source']} and target as {predicate_schema['target']}")
        return node_map    

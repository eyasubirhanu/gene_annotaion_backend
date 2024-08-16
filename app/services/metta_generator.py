import glob
import os
import re
import json
import uuid
from hyperon import MeTTa, SymbolAtom, ExpressionAtom, GroundedAtom
from .query_generator_interface import QueryGeneratorInterface
from app.lib import validate_request

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
        return str(uuid.uuid4())[:8]

    def construct_node_representation(self, node, identifier):
        node_type = node['type']
        # node_representation = ''
        # for key, value in node['properties'].items():
        #     node_representation += f' ({key} ({node_type + " " + identifier}) {value})'
        # return node_representation
        return ' '.join(f'({key} ({node_type} {identifier}) {value})' for key, value in node['properties'].items())


    def query_Generator(self, data, schema):

        node_map = validate_request(data, schema)

        if node_map is None:
            raise Exception('error')

        nodes = data['nodes']

        metta_output = '''!(match &space (,'''
        output = ''' (,'''
 
        node_without_predicate = data.get("predicates") is None or any(
            node["node_id"] not in {p["source"] for p in data.get("predicates", [])} | {p["target"] for p in data.get("predicates", [])}
            for node in nodes
        )
        
        # if there is no predicate
        if node_without_predicate:
            for node in nodes:
                node_type = node["type"]
                node_id = node["node_id"]
                node_identifier = f'${node_id}'
                if node["id"]:
                    essemble_id = node["id"]
                    metta_output += f' ({node_type} {essemble_id})'
                    output += f' ({node_type} {essemble_id})'
                else:
                    if len(node["properties"]) == 0:
                        metta_output += f' ({node_type} {node_identifier})'
                    else:
                        metta_output += self.construct_node_representation(node, node_identifier)
                    output += f' ({node_type} {node_identifier})'
        
        predicates = data.get("predicates")
        if predicates is None:
            return metta_output + '''))'''

        for predicate in predicates:
            predicate_type = predicate['type'].replace(" ", "_")
            source_node = node_map[predicate['source']]
            target_node = node_map[predicate['target']]

            source = self._get_node_representation(source_node, predicate['source'])
            target = self._get_node_representation(target_node, predicate['target'])

            metta_output += f' ({predicate_type} {source} {target})'
            output += f' ({predicate_type} {source} {target})'

        metta_output += f' ){output}))'
        print("metta_output:", metta_output)
        return metta_output

    def _get_node_representation(self, node, node_id):
        if not node['id']:
            node_identifier = f'${node_id}'
            self.construct_node_representation(node, node_identifier)
            return f'({node["type"]} {node_identifier})'
        return f'({node["id"]})'

    def run_query(self, query_code):
        return self.metta.run(query_code)

    def parse_and_serialize(self, input, schema):
        result = []

        tuples = self.metta_seralizer(input[0])
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
        
        query = self.get_node_properties(result, schema)
        result = self.run_query(query)
        result = self.parse_and_serialize_properties(result[0])

        return result
        
    # def parse_metta(self, input_string):
    #     parsed_metta = self.metta.parse_all(input_string)
    #     print("parsed_metta",parsed_metta)
    def parse_and_serialize_properties(self, input):
        nodes = {}
        relationships_dict = {}
        result = []
        tuples = self.metta_seralizer(input)
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
                
                # Skip adding the synonyms property to the node
                if predicate == "synonyms":
                    continue

                if (src_type, src_value) not in nodes:
                    nodes[(src_type, src_value)] = {
                        "id": f"{src_type} {src_value}",
                        "type": src_type,
                    }
                if predicate == "accessions":
                    tgt = tgt.split(" ")
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

        node_list = [{"id": self.generate_id(), "data": node} for node in nodes.values()]
        relationship_list = [{"id": self.generate_id(), "data": relationship} for relationship in relationships_dict.values()]

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

    def recurssive_seralize(self, metta_expression, result):
        for node in metta_expression:
            if isinstance(node, SymbolAtom):
             result.append(node.get_name())
            elif isinstance(node, GroundedAtom):
                result.append(str(node))
            else:
                self.recurssive_seralize(node.get_children(), result)
        return result

    def metta_seralizer(self, metta_result):
        result = []

        for node in metta_result:
            node = node.get_children()
            for metta_symbol in node:
                if isinstance(metta_symbol, SymbolAtom) and  metta_symbol.get_name() == ",":
                    continue
                if isinstance(metta_symbol, ExpressionAtom):
                    res = self.recurssive_seralize(metta_symbol.get_children(), [])
                    result.append(tuple(res))
        return result

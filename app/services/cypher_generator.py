from .query_generator_interface import QueryGeneratorInterface
import json

class Cypher_Query_Generator(QueryGeneratorInterface):
    def query_Generator(data):
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
            return_statements.append('apoc.convert.toJson('+node['node_id']+') AS '+ node['node_id'])

        for predicate in predicates:
            predicate_type = predicate['type'].replace(" ", "_")
            source_id = predicate['source']
            print("source_id", source_id)
            target_id = predicate['target']
            print("target_id", target_id)

            predicate_generated_id =  source_id + "_" + predicate_type + "_" + target_id
            print("predicate_generated_id", predicate_generated_id)

            # get source node
            source_node = nodes[source_id]
            print("source_node", source_node)
            source_node_type = source_node["type"]
            source_node_properties_str = ", ".join([f"{k}: '{v}'" for k, v in source_node["properties"].items()])
            if source_node['id']:
                source_match = f"({source_node['node_id']}:{source_node_type} {{id: '{source_node['id']}'}})"
            else:
                source_match = f"({source_node['node_id']}:{source_node_type} {{{source_node_properties_str}}})"
            
            #get target node
            target_node = nodes[target_id]
            print("target_node", target_node)
            target_node_type = target_node["type"]
            target_node_properties_str = ", ".join([f"{k}: '{v}'" for k, v in target_node["properties"].items()])
            if target_node['id']:
                target_match = f"({target_node['node_id']}:{target_node_type} {{id: '{target_node['id']}'}})"
            else:
                target_match = f"({target_node['node_id']}:{target_node_type} {{{target_node_properties_str}}})"
            return_statements.append('apoc.convert.toJson('+source_node['node_id']+') AS '+ source_node['node_id'])
            return_statements.append('apoc.convert.toJson('+target_node['node_id']+') AS '+ target_node['node_id'])
            return_statements.append('apoc.convert.toJson('+predicate_generated_id+') AS '+ predicate_generated_id)
            match_statement = f" {source_match}-[{predicate_generated_id}:{predicate_type}]->{target_match}"
            match_statements.append(match_statement)
        return_statements = list(set(return_statements))
        match_query = "MATCH " + ", ".join(match_statements)
        return_query = "RETURN " + ", ".join(return_statements)
        cypher_output = f"{match_query} {return_query}"
        print('Cypher: ' , cypher_output)
        return cypher_output

    def parse_and_serialize(input_string: str) -> str:
        cleaned_string = input_string.strip()
        print("Response: ", cleaned_string)
        list_returned = eval(cleaned_string)
        included_ids = []
        nodes = []
        edges = []
        for item in list_returned:
            fields = list(item.values())
            ids_map = {}
            fields_map = {}
            for key, value in item.items():
                if key.endswith("__id"):
                    id = value
                    element = key.split("__")[0]
                    ids_map[element] = id
                    fields_map[id] = item
            for key, value in item.items():
                if not key.endswith("__id"):
                    id = ids_map[key]
                    fields_map[id] = value
            print("IDS: ", ids_map)
            print("Fields: ", fields_map)
            for key, value in fields_map.items():
                if isinstance(value, tuple):
                    source, type, target = value
                    for k, v in fields_map.items():
                        if v == source:
                            source_id = k
                    for k, v in fields_map.items():
                        if v == target:
                            target_id = k
                    if source_id not in included_ids:
                        source_data = {
                            "id": f"{source_type} {source_id}",
                            "label": source_type,
                            "type": source_type,
                            **source_properties
                        }
                        nodes.append(
                        {
                            "data": source_data
                        }
                        )
                else:
                    print("Dict")

            for field in fields:
                if 'type' in field: # if predicate
                    predicate_properties = field['properties'].copy()
                    predicate_id = predicate_properties.pop('id', '')
                    predicate_type = field['type']

                    source_obj = fields_map[field['startNodeElementId']]
                    source_properties = source_obj['properties'].copy()
                    source_id = source_properties.pop('id', '')
                    source_type = source_obj['labels'][0]
                    if field['startNodeElementId'] not in included_ids:   
                        source_data = {
                            "id": f"{source_type} {source_id}",
                            "label": source_type,
                            "type": source_type,
                            **source_properties
                        }
                        nodes.append(
                        {
                            "data": source_data
                        }
                        )
                        included_ids.append(field['startNodeElementId'])
                    target_obj = fields_map[field['endNodeElementId']]
                    target_properties = target_obj['properties'].copy()
                    target_id = target_properties.pop('id', '')
                    target_type = target_obj['labels'][0]
                    if field['endNodeElementId'] not in included_ids:
                        target_data = {
                            "id": f"{target_type} {target_id}",
                            "label": target_type,
                            "type": target_type,
                            **target_properties
                        }
                        nodes.append({
                            "data": target_data
                        })
                        included_ids.append(field['endNodeElementId'])
                    predicate_data = {
                        "id": f"{predicate_type} {predicate_id}",
                        "label": predicate_type,
                        "source": f"{source_type} {source_id}",
                        "target": f"{target_type} {target_id}",
                        **predicate_properties
                    }
                    
                    
                    edges.append({
                        "data": predicate_data
                    })
                    included_ids.append(field['elementId'])
                else:
                    # in case there are no predicates.. 
                    node_properties = field['properties'].copy()
                    node_id = node_properties.pop('id', '')
                    node_type = field['labels'][0]
                    if field['elementId'] not in included_ids:
                        node_data = {
                                "id": f"{node_type} {node_id}",
                                "label": node_type,
                                "type": node_type,
                                **node_properties
                            } 
                        nodes.append(
                            {
                                "data": node_data
                            }
                            )
                        included_ids.append(field['elementId'])
        parsed_data = {
            "nodes": nodes,
            "edges": edges
        }
        print('Json', parsed_data)
        return json.dumps(parsed_data)





# input_data = {"nodes": [
#         {
#             "node_id": "n1",
#             "id": "gene_id",
#             "type": "gene",
#             "properties": {}
#         },
#         {
#             "node_id": "n2",
#             "id": "",
#             "type": "transcript",
#             "properties": {}
#         },
#         {
#             "node_id": "n3",
#             "id": "",
#             "type": "protein",
#             "properties": {
#                 "protein_name": "MKKS"
#             }
#         }
#     ],
#     "predicates": [
#         {
#             "type": "transcribed to",
#             "source": "n1",
#             "target": "n2"
#         },
#         {
#             "type": "translates to",
#             "source": "n2",
#             "target": "n3"
#         }
#     ]
# }
# print(Cypher_Query_Generator.query_Generator(input_data))

# data = """
# [
#     {
#         "n3": {
#             "accessions": ["B3KUQ0", "Q9H6Y9"],
#             "id": "q9nu02",
#             "source": "Uniprot",
#             "protein_name": "ANKE1",
#             "synonyms": ["AGR:HGNC:15803", "..."],
#             "source_url": "https://www.uniprot.org/"
#         },
#         "n2_translates_to_n3__id": 380,
#         "n2_translates_to_n3": (
#             {
#                 "gene_name": "ANKEF1",
#                 "transcript_id": "ENST00000378380.4",
#                 "transcript_name": "ANKEF1-201",
#                 "start": "10035049",
#                 "end": "10058303",
#                 "id": "enst00000378380",
#                 "source": "GENCODE",
#                 "transcript_type": "protein_coding",
#                 "chr": "chr20",
#                 "source_url": "https://www.gencodegenes.org/human/"
#             },
#             "translates_to",
#             {
#                 "accessions": ["B3KUQ0", "Q9H6Y9"],
#                 "id": "q9nu02",
#                 "source": "Uniprot",
#                 "protein_name": "ANKE1",
#                 "synonyms": ["AGR:HGNC:15803", "..."],
#                 "source_url": "https://www.uniprot.org/"
#             }
#         ),
#         "n2__id": 61,
#         "n2": {
#             "gene_name": "ANKEF1",
#             "transcript_id": "ENST00000378380.4",
#             "transcript_name": "ANKEF1-201",
#             "start": "10035049",
#             "end": "10058303",
#             "id": "enst00000378380",
#             "source": "GENCODE",
#             "transcript_type": "protein_coding",
#             "chr": "chr20",
#             "source_url": "https://www.gencodegenes.org/human/"
#         },
#         "n3__id": 242
#     }
# ]

# """

# print(Cypher_Query_Generator.parse_and_serialize(data))
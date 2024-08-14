from .query_generator_interface import QueryGeneratorInterface
import json

class Cypher_Query_Generator(QueryGeneratorInterface):
    def query_Generator(data):
        nodes = {node['node_id']: node for node in data['nodes']}
        predicates = data['predicates']
        match_statements = []
        return_statements = []
        for predicate in predicates:
            predicate_type = predicate['type'].replace(" ", "_")
            source_id = predicate['source']
            print("source_id", source_id)
            target_id = predicate['target']
            print("target_id", target_id)

            # get source node
            source_node = nodes[source_id]
            print("source_node", source_node)
            source_node_type = source_node["type"]
            source_node_properties_str = ", ".join([f"{k}: '{v}'" for k, v in source_node["properties"].items()])
            if source_node['id']:
                source_match = f"({source_node['node_id']}:{source_node_type} {{id: '{source_node['id']}'}})"
            else:
                source_match = f"({source_node['node_id']}:{source_node_type} {source_node_properties_str})"
            
            #get target node
            target_node = nodes[target_id]
            print("target_node", target_node)
            target_node_type = target_node["type"]
            target_node_properties_str = ", ".join([f"{k}: '{v}'" for k, v in target_node["properties"].items()])
            if target_node['id']:
                target_match = f"({target_node['node_id']}:{target_node_type} {{id: '{target_node['id']}'}})"
            else:
                target_match = f"({target_node['node_id']}:{target_node_type} {target_node_properties_str})"
            return_statements.append(source_node['node_id'])
            return_statements.append(target_node['node_id'])
            return_statements = list(set(return_statements))
            match_statement = f" {source_match}-[:{predicate_type}]-{target_match}"
            match_statements.append(match_statement)
        match_query = "MATCH " + ", ".join(match_statements)
        return_query = "RETURN " + ", ".join(return_statements)
        cypher_output = f"{match_query} {return_query}"
        return cypher_output

    def parse_and_serialize(input_string: str) -> str:
        cleaned_string = input_string.strip()
        list_returned = eval(cleaned_string)
        included_ids = []
        nodes = []
        edges = []
        for item in list_returned:
            fields = list(item.values())
            fields_map = {}
            for field in fields:
                fields_map[field['elementId']] = field
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

# input = """
# [
#   {
#     "n": {
#       "identity": 884,
#       "labels": [
#         "gene"
#       ],
#       "properties": {
#         "gene_name": "PAK5",
#         "gene_type": "protein_coding",
#         "synonyms": [
#           "p21CDKN1A-activated kinase 7",
#           "PAK-7",
#           "serine/threonine-protein kinase PAK7",
#           "PAK7",
#           "p21(CDKN1A)-activated kinase 7",
#           "PAK-5",
#           "p21-activated kinase 7",
#           "p21 protein (Cdc42/Rac)-activated kinase 7",
#           "protein kinase PAK5",
#           "p21 (RAC1) activated kinase 5",
#           "serine/threonine-protein kinase PAK 5",
#           "p21-activated kinase 5",
#           "serine/threonine-protein kinase PAK 7",
#           "HGNC:15916",
#           "PAK5",
#           "p21 (RAC1) activated kinase 7"
#         ],
#         "start": "9537370",
#         "end": "9839076",
#         "source": "GENCODE",
#         "id": "ensg00000101349",
#         "chr": "chr20",
#         "source_url": "https://www.gencodegenes.org/human/"
#       },
#       "elementId": "4:fb3bf8c9-deff-44c2-81ff-c36c561d2984:884"
#     },
#     "r": {
#       "identity": 0,
#       "start": 884,
#       "end": 936,
#       "type": "transcribed_to",
#       "properties": {
#         "source": "GENCODE",
#         "source_url": "https://www.gencodegenes.org/human/"
#       },
#       "elementId": "5:fb3bf8c9-deff-44c2-81ff-c36c561d2984:0",
#       "startNodeElementId": "4:fb3bf8c9-deff-44c2-81ff-c36c561d2984:884",
#       "endNodeElementId": "4:fb3bf8c9-deff-44c2-81ff-c36c561d2984:936"
#     },
#     "b": {
#       "identity": 936,
#       "labels": [
#         "transcript"
#       ],
#       "properties": {
#         "gene_name": "PAK5",
#         "transcript_id": "ENST00000353224.10",
#         "transcript_name": "PAK5-201",
#         "start": "9537370",
#         "end": "9839076",
#         "source": "GENCODE",
#         "id": "enst00000353224",
#         "transcript_type": "protein_coding",
#         "chr": "chr20",
#         "source_url": "https://www.gencodegenes.org/human/"
#       },
#       "elementId": "4:fb3bf8c9-deff-44c2-81ff-c36c561d2984:936"
#     }
#   }]
# """

# print(Cypher_Query_Generator.parse_and_serialize(input))
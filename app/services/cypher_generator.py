from .query_generator_interface import QueryGeneratorInterface

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
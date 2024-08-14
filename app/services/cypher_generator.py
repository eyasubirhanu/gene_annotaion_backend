from .query_generator_interface import QueryGeneratorInterface
import json

class Cypher_Query_Generator(QueryGeneratorInterface):
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

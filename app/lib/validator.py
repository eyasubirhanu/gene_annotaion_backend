def validate_request(request, schema):
    # Check if 'nodes' is in the request
    if 'nodes' not in request:
        raise ValueError("The 'nodes' field is missing in the request.")

    nodes = request['nodes']
    
    # Validate 'nodes' field
    if not isinstance(nodes, list):
        raise ValueError("'nodes' should be a list.")

    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError("Each node must be a dictionary.")
        if 'id' not in node:
            raise ValueError("Each node requires an 'id' field.")
        if 'type' not in node or node['type'] == "":
            raise ValueError("Each node requires a 'type' field.")
        if 'node_id' not in node or node['node_id'] == "":
            raise ValueError("Each node requires a 'node_id' field.")
        if 'properties' not in node:
            raise ValueError("Each node requires a 'properties' field.")
        
    # Validate the properties of each node
    for node in nodes:
        properties = node['properties']
        node_type = node['type']
        
        # Check if the node type exists in the schema
        if node_type not in schema:
            raise ValueError(f"Node type '{node_type}' not found in the schema.")
        
        # Validate properties of the node against the schema
        for property in properties.keys():
            if property not in schema[node_type]['properties']:
                raise ValueError(f"Property '{property}' doesn't exist in the schema for node type '{node_type}'.")
    
    node_map = {node['node_id']: node for node in nodes}

    # Validate 'predicates' field if present
    if 'predicates' in request:
        predicates = request['predicates']
        
        if not isinstance(predicates, list):
            raise ValueError("'predicates' should be a list.")
        
        for predicate in predicates:
            if 'type' not in predicate or predicate['type'] == "":
                raise ValueError("Each predicate requires a 'type' field.")
            if 'source' not in predicate or predicate['source'] == "":
                raise ValueError("Each predicate requires a 'source' field.")
            if 'target' not in predicate or predicate['target'] == "":
                raise ValueError("Each predicate requires a 'target' field.")

            if predicate['source'] not in node_map:
                raise ValueError(f"Source node '{predicate['source']}' does not exist in the 'nodes' object.")
            if predicate['target'] not in node_map:
                raise ValueError(f"Target node '{predicate['target']}' does not exist in the 'nodes' object.")

            # Validate predicate schema
            predicate_schema = schema[predicate['type']]
            source_type = node_map[predicate['source']]['type']
            target_type = node_map[predicate['target']]['type']

            if predicate_schema['source'] != source_type or predicate_schema['target'] != target_type:
                raise ValueError(f"Predicate '{predicate['type']}' has source '{predicate_schema['source']}' and target '{predicate_schema['target']}', but was given source '{source_type}' and target '{target_type}'.")

    return node_map

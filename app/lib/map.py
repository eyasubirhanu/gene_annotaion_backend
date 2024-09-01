def map_node(graph):
    nodes = graph["nodes"]
    edges = graph["edges"]

    # Create a mapping of node IDs to their indices
    node_id_to_index = {node["data"]["id"]: idx for idx, node in enumerate(nodes)}
    
    # Initialize edge_idx with empty lists for each node
    edge_indices = [[] for _ in range(len(nodes))]
    single_node_idx = []

    # Track nodes that have edges
    has_edges = [False] * len(nodes)

    # Process edges and populate edge_indices
    for edge_index, edge in enumerate(edges):
        source_id = edge["data"]["source"]
        target_id = edge["data"]["target"]

        if source_id in node_id_to_index:
            source_index = node_id_to_index[source_id]
            edge_indices[source_index].append(edge_index)
            has_edges[source_index] = True

        if target_id in node_id_to_index:
            target_index = node_id_to_index[target_id]
            has_edges[target_index] = True

    # Determine nodes without edges
    for idx, has_edge in enumerate(has_edges):
        if not has_edge:
            single_node_idx.append(idx)
    return edge_indices, single_node_idx


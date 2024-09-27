import re

def parse_search(search: str) -> dict:

    search_list = re.findall('\((\w+)\s+\((\w+)\s(\w+)\)\s(\$\w+)\)',search)
    long_search = re.findall('\((\w+)\s\((\w+)\s+\((\w+)\s(\w+)\)\s\((\w+)\s(\w+)\)\)\s(\$\w+)\)', search)
    for long in long_search:
        search_list.append(long)
    
    search_dict = {}
    for s in search_list:
        if len(s) == 4:
            predicate, node_type, node_id, node_var = s
            if node_type not in search_dict.keys():
                search_dict[node_type] = {}
            if node_id not in search_dict[node_type].keys():
                search_dict[node_type][node_id] = [(predicate, node_var)]
            else:
                search_dict[node_type][node_id].append((predicate, node_var))
        if len(s) == 7:
            predicate, edge, source_type, source_id, tgt_type, tgt_id, node_var = s
            key = f'{edge}'
            id_key = f'{source_id} {tgt_id}'
            if key not in search_dict.keys():
                search_dict[key] = {}
            if id_key not in search_dict[key].keys():
                search_dict[key][id_key] = [(predicate, source_type, tgt_type, node_var)]
            else:
                search_dict[key][id_key].append((predicate, source_type, tgt_type, node_var))
    return search_dict

def parse_match(match:str, schema) -> bool:

    match_list = re.findall('\((\w+)\s(\w+)\s+\((\w+)\s(\w+)\)\s(\$\w+)\)',match)
    long_search = re.findall('\((\w+)\s(\w+)\s\((\w+)\s\((\w+)\s(\w+)\)\s\((\w+)\s(\w+)\)\)\s([$\w]+)\)', match)
    for long in long_search:
        match_list.append(long)

    match_dict = {}        
    for m in match_list:
        if len(m) == 5:
            represented_as, predicate, node_type, node_id, node_var = m
            if represented_as != schema[node_type]['represented_as']:
                raise Exception(f'node type {node_type} can not be an {represented_as}')
            if node_type not in match_dict.keys():
                match_dict[node_type] = {}
            if node_id not in match_dict[node_type].keys():
                match_dict[node_type][node_id] = [(predicate, node_var)]
            else:
                match_dict[node_type][node_id].append((predicate, node_var))
        if len(m) == 8:
            represented_as, predicate, edge, source_type, source_id, tgt_type, tgt_id, node_var  = m
            search_edge = edge.replace('_', ' ')
            if represented_as != schema[search_edge]['represented_as']:
                raise Exception(f'node type {node_type} can not be an {represented_as}')
            if edge not in match_dict.keys():
                match_dict[edge] = {}
            key = f'{source_id} {tgt_id}'
            if key not in match_dict[edge].keys():
                match_dict[edge][key] = [(predicate, source_type, tgt_type, node_var)]
            else:
                match_dict[edge][key].append((predicate, source_type, tgt_type, node_var))
    return match_dict

def parse_node(output:str, schema) -> bool:

    # remove the prefix
    output = output.removeprefix("!(match &space")
    
    # split the match query string into the query and the expected output
    out_list = re.findall('(\(,[()\w\s$]+\))', output)
    search, match = out_list
    
    # parse the search and match into a dict of structure
    # {'type':{'id':[('property', 'variable'),...],...}...}
    parsed_source = parse_search(search)
    try:
        parsed_match = parse_match(match, schema)
    except (Exception) as e:
        return e
    
    return parsed_source == parsed_match
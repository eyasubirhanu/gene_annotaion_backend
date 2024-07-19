import logging
from .schema_data import SchemaManager
from biocypher import BioCypher

def validate_request(requests): 
    bcy = BioCypher(schema_config_path='./config/schema_config.yaml')
    schema = bcy._get_ontology_mapping()._extend_schema()
    nodes = requests.get('nodes', [])
    predicates = requests.get('predicates', [])

    if not nodes or not predicates:
        logging.debug("Request is missing nodes or predicates.")
        return False, "Request is missing nodes or predicates."

    node_dict = {node['node_id']: node for node in nodes}

    for node in nodes:
        if not node['node_id'] or not node['type'] or not node.get('id'):
            logging.debug(f"Node missing required fields: {node}")
            return False, f"Node missing required fields: {node}"

    for predicate in predicates:
        if not predicate.get('type') or not predicate.get('source') or not predicate.get('target'):
            logging.debug(f"Predicate missing required fields: {predicate}")
            return False, f"Predicate missing required fields: {predicate}"
        
        if predicate.get('source') not in node_dict:
            logging.debug(f"Predicate source node not found: {predicate['source']}")
            return False, f"Predicate source node not found: {predicate['source']}"

        if predicate.get('target') not in node_dict:
            logging.debug(f"Predicate target node not found: {predicate['target']}")
            return False, f"Predicate target node not found: {predicate['target']}"
        
        # Validate predicate types
        predicate_type = predicate['type']
        if predicate_type not in schema:
            return False, f"Predicate {predicate_type} not in schema"

        pred_schema = schema[predicate_type]
        source_node = node_dict[predicate['source']]
        target_node = node_dict[predicate['target']]

        if source_node['type'] != pred_schema['source']:
            return False, f"Source type mismatch: expected {pred_schema['source']}, got {source_node['type']}"

        if target_node['type'] != pred_schema['target']:
            return False, f"Target type mismatch: expected {pred_schema['target']}, got {target_node['type']}"

    return True, ""
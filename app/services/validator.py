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
        if not node['node_id'] or not node['type']:
            logging.debug(f"Node missing required fields: {node}")
            return False, f"Node missing required fields: {node}"

    for predicate in predicates:
        if not predicate['type'] or not predicate['source'] or not predicate['target']:
            logging.debug(f"Predicate missing required fields: {predicate}")
            return False, f"Predicate missing required fields: {predicate}"
        
        if predicate['source'] not in node_dict:
            logging.debug(f"Predicate source node not found: {predicate['source']}")
            return False, f"Predicate source node not found: {predicate['source']}"

        if predicate['target'] not in node_dict:
            logging.debug(f"Predicate target node not found: {predicate['target']}")
            return False, f"Predicate target node not found: {predicate['target']}"

        if 'type' not in schema or predicate['type'] not in schema:
            logging.debug(f"Predicate type {predicate['type']} not in schema")
            return False, f"Predicate type {predicate['type']} not in schema"

    def check_predicate(node_dict, predicate, schema):
        predicate_type = predicate['type']
        logging.debug(f"Validating predicate: {predicate_type}")

        if predicate_type not in schema:
            logging.debug(f"Predicate {predicate_type} not in schema")
            return False, f"Predicate {predicate_type} not in schema"

        pred_schema = schema[predicate_type]
        source_node = node_dict[predicate['source']]
        target_node = node_dict[predicate['target']]

        if not source_node or not target_node:
            logging.debug(f"Predicate source or target node not found: {predicate}")
            return False, f"Predicate source or target node not found: {predicate}"

        if source_node['type'] != pred_schema['source']:
            logging.debug(f"Source type mismatch: expected {pred_schema['source']}, got {source_node['type']}")
            return False, f"Source type mismatch: expected {pred_schema['source']}, got {source_node['type']}"

        if target_node['type'] != pred_schema['target']:
            logging.debug(f"Target type mismatch: expected {pred_schema['target']}, got {target_node['type']}")
            return False, f"Target type mismatch: expected {pred_schema['target']}, got {target_node['type']}"

        return True, ""

    for predicate in predicates:
        is_valid, message = check_predicate(node_dict, predicate, schema)
        if not is_valid:
            logging.debug(f"Predicate validation failed: {predicate}")
            return False, message
        
    return True, ""

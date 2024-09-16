from flask import Flask, request, jsonify, Response, send_from_directory
import logging
import json
from app import app, databases, schema_manager
import configparser
import os
from app.lib import GraphProcessor
from flask_cors import CORS
from app.lib import limit_node

#enable cors
CORS(app)
# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

# Load the config file
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)

# Check if the file is read correctly
if not config.read(config_path):
    logging.error(f"Config file not found at: {config_path}")
    raise FileNotFoundError(f"Config file found at: {config_path}")

@app.route('/nodes')
def get_nodes_endpoint():
    nodes = json.dumps(schema_manager.get_nodes(), indent=4)
    return Response(nodes, mimetype='application/json')

@app.route('/swagger.json')
def swagger():
    with open('./swagger.json', 'r') as f:
        return jsonify(json.load(f))

@app.route('/edges', methods=['GET'])
def get_edges_endpoint():
    edges = json.dumps(schema_manager.get_edges(), indent=4)
    return Response(edges, mimetype='application/json')

@app.route('/relations/<node_label>', methods=['GET'])
def get_relations_for_node_endpoint(node_label):
    relations = json.dumps(schema_manager.get_relations_for_node(node_label), indent=4)
    return Response(relations, mimetype='application/json')

@app.route('/query', methods=['POST'])
def process_query():
    data = request.get_json()
    if not data or 'requests' not in data:
        return jsonify({"error": "Missing requests data"}), 400
    database_type = config['database']['type']# data.get('database')
    # if not database_type or database_type not in databases:
    #     return jsonify({"error": "Invalid or missing database parameter"}), 400
    try:
        db_instance = databases[database_type]
        requests = data['requests']
        query_code = db_instance.query_Generator(requests, schema_manager.schema)
        result = db_instance.run_query(query_code)
        parsed_result = db_instance.parse_and_serialize(result, schema_manager.schema)
        response = limit_node(parsed_result, 30)
        result_json = json.dumps(response)
        graph_processor = GraphProcessor(result_json)
        result = graph_processor.process()
        #formatted_response = json.dumps(result, indent=None) # removed indent=4 because am getting /n on the response
        return Response(result, mimetype='application/json')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


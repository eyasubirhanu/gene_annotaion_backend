from flask import Flask, request, jsonify, session, Response
import logging
import json
from app import app, databases, schema_manager
import itertools
from flask_cors import CORS
from functools import wraps

CORS(app)

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return jsonify({"error": "Unauthorized access. Please log in."}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/nodes', methods=['GET'])
@login_required
def get_nodes_endpoint():
    nodes = json.dumps(schema_manager.get_nodes(), indent=4)
    return Response(nodes, mimetype='application/json')

@app.route('/edges', methods=['GET'])
@login_required
def get_edges_endpoint():
    edges = json.dumps(schema_manager.get_edges(), indent=4)
    return Response(edges, mimetype='application/json')

@app.route('/relations/<node_label>', methods=['GET'])
@login_required
def get_relations_for_node_endpoint(node_label):
    relations = json.dumps(schema_manager.get_relations_for_node(node_label), indent=4)
    return Response(relations, mimetype='application/json')

@app.route('/query', methods=['POST'])
@login_required
def process_query():
    data = request.get_json()
    if not data or 'requests' not in data:
        return jsonify({"error": "Missing requests data"}), 400
    database_type = 'metta'# data.get('database')
    # if not database_type or database_type not in databases:
    #     return jsonify({"error": "Invalid or missing database parameter"}), 400
    try:
        db_instance = databases[database_type]
        requests = data['requests']
        query_code = db_instance.query_Generator(requests, schema_manager.schema)
        result = db_instance.run_query(query_code)
        parsed_result = db_instance.parse_and_serialize(result, schema_manager.schema)
            
        response_data = {
            # "Generated query": query_code,
            "nodes": parsed_result[0],
            "edges": parsed_result[1]
        }
        formatted_response = json.dumps(response_data, indent=4) # removed indent=4 because am getting /n on the response
        return Response(formatted_response, mimetype='application/json')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

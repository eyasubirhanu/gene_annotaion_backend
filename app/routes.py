from flask import Flask, request, jsonify, Response
import logging
import json
from app import app, databases, schema_manager, chatbots
import itertools
from app.lib import validate_request 
from app.services.annotation_graph import process_graph
# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/nodes', methods=['GET'])
def get_nodes_endpoint():
    nodes = json.dumps(schema_manager.get_nodes(), indent=4)
    return Response(nodes, mimetype='application/json')

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

    try:
        requests = data['requests']
        
        # Validate the request data before processing
        node_map = validate_request(requests, schema_manager.schema)
        
        database_type = 'cypher'
        db_instance = databases[database_type]
        
        # Generate the query code
        query_code = db_instance.query_Generator(requests, node_map)
        
        # Run the query and parse the results
        result = db_instance.run_query(query_code)
        parsed_result = db_instance.parse_and_serialize(result, schema_manager.schema)
        
        response_data = {
            "nodes": parsed_result[0],
            "edges": parsed_result[1]
        }
        # formatted_response = json.dumps(response_data, indent=4)
        
        annotation_graph_data = json.dumps(response_data)
        annotation_graph = process_graph(annotation_graph_data)
        formatted_response = json.dumps(annotation_graph, indent=4)
        
        return Response(formatted_response, mimetype='application/json')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing prompt"}), 400

    try:
        prompt = data['prompt'] 
        chatbot_type = 'groq'
        chatbot_instance = chatbots[chatbot_type]
        print(chatbot_type)
        output = chatbot_instance.run_user_input(prompt)
        response = {
            "chat": output[0],
            "graph": output[1]
        }
        print(output)
        formatted_response = json.dumps(output, indent=4)
        print(formatted_response)
        return Response(formatted_response, mimetype='application/json')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

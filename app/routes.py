from flask import Flask, request, jsonify, Response
from flask_restx import Resource, Namespace, fields
from app import api, schema_manager, app, databases
import logging
import json
import itertools
from app.lib import validate_request


# Setup basic logging
logging.basicConfig(level=logging.DEBUG)


edges_ns = Namespace("edges", description="Edges related operations")


@edges_ns.route("/")
class EdgeList(Resource):
    @edges_ns.doc("list_edges")
    def get(self):
        """List all edges"""
        edges = json.dumps(schema_manager.get_edges(), indent=4)
        return Response(edges, mimetype="application/json")


nodes_ns = Namespace("nodes", description="nodes related operations")


@nodes_ns.route("/")
class NodeList(Resource):
    @nodes_ns.doc("list_nodes")
    def get(self):
        """List all nodes"""
        nodes = json.dumps(schema_manager.get_nodes(), indent=4)
        return Response(nodes, mimetype="application/json")


relations_ns = Namespace("relations", description="Relationships between nodes")


@relations_ns.route("/<node_label>")
class NodeRelations(Resource):
    @relations_ns.doc("get_relations_for_node")
    def get(self, node_label):
        """Get relations for a specific node"""
        relations = json.dumps(
            schema_manager.get_relations_for_node(node_label), indent=4
        )
        return Response(relations, mimetype="application/json")


query_ns = Namespace("query", description="Query processing operations")
query_model = api.model(
    "query",
    {
        "requests": fields.String(required=True, description="The request details"),
        "node_map": fields.String(description="Node mapping details."),
        "db_type": fields.String(description="Database type"),
    },
)


@query_ns.route("/")
class ProcessQuery(Resource):
    @query_ns.expect(query_model)
    @query_ns.doc("process_query")
    def post(self):
        """Process query"""
        data = requests.get_json()
        if not data or "requests" not in data:
            return jsonify({"error": "Missing requests data"}), 400

        try:
            requests = data["requests"]
            node_map = data.get("node_map", {})
            database_type = data.get("db_type", "cypher")
            db_instance = databases[database_type]

            query_code = db_instance.query_Generator(requests, node_map)

            result = db_instance.run_query(query_code)
            parsed_result = db_instance.parse_and_serialize(
                result, schema_manager.schema
            )

            response_data = {"nodes": parsed_result[0], "edges": parsed_result[1]}
            return jsonify(response_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500


api.add_namespace(edges_ns, path="/edges")
api.add_namespace(nodes_ns, path="/nodes")
api.add_namespace(relations_ns, path="/relations")
api.add_namespace(query_ns, path="/query")


"""@app.route("/nodes", methods=["GET"])
def get_nodes_endpoint():
    nodes = json.dumps(schema_manager.get_nodes(), indent=4)
    return Response(nodes, mimetype="application/json")


@app.route("/edges", methods=["GET"])
def get_edges_endpoint():
    edges = json.dumps(schema_manager.get_edges(), indent=4)
    return Response(edges, mimetype="application/json")


@app.route("/relations/<node_label>", methods=["GET"])
def get_relations_for_node_endpoint(node_label):
    relations = json.dumps(schema_manager.get_relations_for_node(node_label), indent=4)
    return Response(relations, mimetype="application/json")



@app.route("/query", methods=["POST"])
def process_query():
    data = request.get_json()
    if not data or "requests" not in data:
        return jsonify({"error": "Missing requests data"}), 400

    try:
        requests = data["requests"]

        # Validate the request data before processing
        node_map = validate_request(requests, schema_manager.schema)

        database_type = "cypher"
        db_instance = databases[database_type]

        # Generate the query code
        query_code = db_instance.query_Generator(requests, node_map)

        # Run the query and parse the results
        result = db_instance.run_query(query_code)
        parsed_result = db_instance.parse_and_serialize(result, schema_manager.schema)

        response_data = {"nodes": parsed_result[0], "edges": parsed_result[1]}

        formatted_response = json.dumps(response_data, indent=4)
        return Response(formatted_response, mimetype="application/json")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""

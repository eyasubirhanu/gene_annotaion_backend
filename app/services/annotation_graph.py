import ann_graph
import tempfile, os


def process_graph(json_string: str):
    temp_dir = '/tmp/annotation_graph'
    os.makedirs(temp_dir, exist_ok=True)    
    input_file_path = os.path.join(temp_dir, "input.json")
    output_file_path = os.path.join(temp_dir, "nongo.json")
    # Get the path of the temporary file
    # temp_file_path = temp_file.name

    with open(input_file_path, 'w') as file:
        print("Opened input file: ", input_file_path)

        file.write(json_string)
    # Create a GraphProcessor instance
    try:
        processor = ann_graph.GraphProcessor(input_file_path)

        # Write JSON to the temporary file
        processor.process()

        # Read the JSON content from the temporary file
        with open(output_file_path, 'r') as file:
            json_data = file.read()

        return json_data
    except Exception as e:
        print(f"Couldn't finish building graph {e}")
        return "{}"
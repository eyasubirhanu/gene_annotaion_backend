import unittest
from unittest.mock import MagicMock, patch
from app.services.metta_generator import MeTTa_Query_Generator


class TestMeTTaQueryGenerator(unittest.TestCase):

    def setUp(self):
        self.query_generator = MeTTa_Query_Generator(dataset_path="./metta_data")

    def test_initialize_space(self):
        self.query_generator.metta.run = MagicMock()
        self.query_generator.initialize_space()
        self.query_generator.metta.run.assert_called_with("!(bind! &space (new-space))")

    @patch("app.services.metta_generator.glob.glob")
    @patch("app.services.metta_generator.os.path.exists")
    @patch("app.services.metta_generator.logging")
    def test_load_dataset(self, mock_logging, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = ["/path/to/dataset.metta"]
        self.query_generator.metta.run = MagicMock()

        self.query_generator.load_dataset("/path/to/dataset")

        mock_exists.assert_called_with("/path/to/dataset")
        mock_glob.assert_called_with("/path/to/dataset/**/*.metta", recursive=True)

        actual_call = self.query_generator.metta.run.call_args[0][0].strip()
        expected_call = "!(load-ascii &space /path/to/dataset.metta)"

        self.assertEqual(actual_call, expected_call)

    def test_generate_id(self):
        result = self.query_generator.generate_id()
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 8)

    def test_construct_node_representation(self):
        node = {"type": "gene", "properties": {"gene_type": "protein_coding"}}
        identifier = "$n1"
        result = self.query_generator.construct_node_representation(node, identifier)
        expected_result = " (gene_type (gene $n1) protein_coding)"
        self.assertEqual(result, expected_result)

    def test_query_Generator(self):
        data = {
            "nodes": [
                {
                    "node_id": "n1",
                    "type": "gene",
                    "properties": {"gene_type": "protein_coding"},
                },
                {"node_id": "n2", "type": "transcript", "properties": {}},
                {
                    "node_id": "n3",
                    "type": "protein",
                    "properties": {"protein_name": "MKKS"},
                },
                {
                    "node_id": "n4",
                    "type": "protein",
                    "properties": {"protein_name": "ANKE1"},
                },
            ],
            "predicates": [
                {"type": "transcribed to", "source": "n1", "target": "n2"},
                {"type": "translates to", "source": "n2", "target": "n3"},
            ],
        }
        node_map = {
            "n1": {
                "node_id": "n1",
                "type": "gene",
                "properties": {"gene_type": "protein_coding"},
            },
            "n2": {"node_id": "n2", "type": "transcript", "properties": {}},
            "n3": {
                "node_id": "n3",
                "type": "protein",
                "properties": {"protein_name": "MKKS"},
            },
            "n4": {
                "node_id": "n4",
                "type": "protein",
                "properties": {"protein_name": "ANKE1"},
            },
        }
        result = self.query_generator.query_Generator(data, node_map)
        expected_result = "!(match &space (, (protein_name (protein $n4) ANKE1) (gene_type (gene $n1) protein_coding) (transcribed_to (gene $n1) (transcript $n2)) (protein_name (protein $n3) MKKS) (translates_to (transcript $n2) (protein $n3)) ) (, (protein $n4) (transcribed_to (gene $n1) (transcript $n2)) (translates_to (transcript $n2) (protein $n3))))"

        self.assertEqual(result, expected_result)

    def test_run_query(self):
        self.query_generator.metta.run = MagicMock(return_value="Result")
        result = self.query_generator.run_query("QUERY")
        self.assertEqual(result, "Result")


if __name__ == "__main__":
    unittest.main()

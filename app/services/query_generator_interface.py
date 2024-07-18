from abc import ABC, abstractmethod

class QueryGeneratorInterface(ABC):
    @abstractmethod
    def query_Generator(self, requests, schema):
        pass

    @abstractmethod
    def run_query(self, query_code):
        pass

    @abstractmethod
    def parse_and_serialize(self, input):
        pass

    @abstractmethod
    def parse_and_serialize_properties(self, input_string):
        pass

    @abstractmethod
    def get_node_properties(self, results, schema):
        pass

    @abstractmethod
    def validate_request(self, request, schema):
        pass

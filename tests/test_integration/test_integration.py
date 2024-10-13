import json
import logging
from app import app
app.logger.disabled = True
logging.getLogger('werkzeug').disabled = True
logging.basicConfig(level=logging.DEBUG)

def test_process_query(query_list, schema):
    # make a call to the /query endpoint

    with app.test_client() as client:
        response = client.post('/query', data=json.dumps(query_list), content_type='application/json')
        assert response._status == '200 OK'
        
        # test output dict keys
        response_json = response.get_json()
        assert tuple(response_json.keys()) == ('nodes', "edges")

        # test the nodes response value is a list
        assert isinstance(response_json['nodes'], list) == True
        assert isinstance(response_json['edges'], list) == True

        i = 0
        # check the schema of the first 10 nodes responses
        while i < len(response_json['nodes']) and i < 10:
            value = response_json['nodes'][i]
            assert isinstance(value, dict)
            keys = list(schema[value['data']['type']]['properties'].keys())
            keys.append('id')
            keys.append('type')
            if 'synonyms' in keys:
                keys.remove('synonyms')
            assert keys.sort() == list(value['data'].keys()).sort()
            i += 1
                
        i = 0
        while i < len(response_json['edges']) and i < 10:
            value = response_json['edges'][i]
            assert isinstance(value, dict)
            keys = ["label", "source", "target", "source_data", "source_url"]
            assert keys.sort() == list(value['data'].keys()).sort()
            i += 1

        
import os, libfa, tokenize_api
from flask import Flask, json, request
from flask_cors import CORS
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from elasticsearch.exceptions import NotFoundError

# set environment
stage_identifier = libfa.get_stage_identifier()
stage_config = libfa.get_stage_configuration(stage_identifier)
print('stage_identifier:', stage_identifier)

# set elasticsearch client
es = Elasticsearch(
        [{'host': stage_config['elasticsearch']['ip'], 'port': stage_config['elasticsearch']['port']}], timeout=300,
        http_auth=(stage_config['elasticsearch']['username'], stage_config['elasticsearch']['password'])
    )
indices_client = IndicesClient(es)

# set flask application
tokenize_api_server = Flask(__name__)

# set CORS origins
tokenize_api_server.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(tokenize_api_server, resources={r'/*': {'origins': '*'}})

# set max content length
tokenize_api_server.config['MAX_CONTENT_LENGTH'] = 2048 * 1024 * 1024


@tokenize_api_server.route('/tokenize', methods=['GET', 'POST'])
def tokenize():
    if request.method == 'GET':
        print('request method: GET')
        text = request.args.get('text')

        if text is None:
            text = ''
    elif request.method == 'POST':
        print('request method: POST')
        # print('[POST]', request.values)

        if 'text' in request.values:
            text = request.values['text']
        else:
            text = ''

    if len(text) > 0:
        tokenized_text = tokenize_api.tokenize_text(text, stage_config=stage_config, indices_client=indices_client)
    else:
        tokenized_text = text
    print('tokenized_text:', tokenized_text)

    response = tokenize_api_server.response_class(
        response=json.dumps({
            'tokenized_text': tokenized_text
        }),
        status=200,
        mimetype='application/json',
    )

    response.headers['Access-Control-Allow-Origin'] = '*'

    return response


if __name__ == '__main__':
    print('tokenize_api_server')

    # initialize tokenizer
    initialize_tokenizer(stage_config=stage_config, es=es, download_nltk_resources=False)

    # run api server
    tokenize_api_port = libfa.get_stage_values('api')['port']
    tokenize_api_server.run(host='0.0.0.0', port=int(tokenize_api_port), debug=False)

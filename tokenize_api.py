import re, requests, json, nltk

# 초성(00 ~ 18)
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
# 중성(00 ~ 20)
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
# 종성(00 ~ 27 + 1(1: 없음))
JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']


def split_by_languages(string):
    alphanumeric = ''
    korean = ''
    chinese = ''
    japanese = ''

    for char in string:
        if re.search(r'\s', char):
            alphanumeric += ' '
            korean += ' '
            chinese += ' '
        elif ord('가') <= ord(char) <= ord('힣'):  # match korean
            korean += char
        elif ord(u'\u4e00') <= ord(char) <= ord(u'\u9fff'):  # match chinese
            chinese += char
        elif ord(u'\u3040') <= ord(char) <= ord(u'\u30ff'):  # match japanese
            japanese += char
        else:
            alphanumeric += char

    alphanumeric = re.sub(r'\s+', ' ', alphanumeric.strip())
    korean = re.sub(r'\s+', ' ', korean.strip())
    chinese = re.sub(r'\s+', ' ', chinese.strip())
    japanese = re.sub(r'\s+', ' ', japanese.strip())

    return {
        'alphanumeric': alphanumeric,
        'korean': korean,
        'chinese': chinese,
        'japanese': japanese
    }


def initialize_tokenizer(stage_config=None, es=None, download_nltk_resources=False):
    ''' Initialize NLTK, NORI Tokenizers '''

    ''' Download NLTK Resources '''
    if download_nltk_resources:
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')

    ''' Check Tokenizer for Korean (`fastapi-tokenizer-korean`) '''
    # delete `fastapi-tokenizer-korean` index if exists
    if es.indices.exists(index='fastapi-tokenizer-korean'):
        es.indices.delete(index='fastapi-tokenizer-korean')

    # put `fastapi-tokenizer-korean` index
    body = {
        'settings': {
            'index': {
                'analysis': {
                    'analyzer': {
                        'fastapi-tokenizer-korean': {
                            'tokenizer': 'nori_tokenizer',
                            'filter': [
                                'my_posfilter'
                            ]
                        }
                    },
                    'filter': {
                        'my_posfilter': {
                            'type': 'nori_part_of_speech',
                            'stoptags': ['E', 'IC', 'J', 'MAG', 'MAJ', 'MM', 'NA', 'NR', 'SC', 'SE', 'SF', 'SH', 'SL', 'SN', 'SP', 'SSC', 'SSO', 'SY', 'UNA', 'UNKNOWN', 'VA', 'VCN', 'VCP', 'VSV', 'VV', 'VX', 'XPN', 'XR', 'XSA', 'XSN', 'XSV']
                        }
                    }
                }
            }
        }
    }
    r = requests.put('http://{elasticsearch_host}:{elasticsearch_port}/fastapi-tokenizer-korean'.format(elasticsearch_host=stage_config['elasticsearch']['ip'], elasticsearch_port=stage_config['elasticsearch']['port']),
                     auth=(stage_config['elasticsearch']['username'], stage_config['elasticsearch']['password']), headers={'Content-Type': 'application/json'},
                     data=json.dumps(body))
    print('re-create `fastapi-tokenizer-korean`:', r.json())

    ''' Check Tokenizer for Chinese, Japanese (`fastapi-tokenized`)'''
    # put `fastapi-tokenized` index if exists
    if es.indices.exists(index='fastapi-tokenized'):
        es.indices.delete(index='fastapi-tokenized')

    # put `fastapi-tokenized` index
    r = requests.put('http://{elasticsearch_host}:{elasticsearch_port}/fastapi-tokenized'.format(elasticsearch_host=stage_config['elasticsearch']['ip'], elasticsearch_port=stage_config['elasticsearch']['port']),
                     auth=(stage_config['elasticsearch']['username'], stage_config['elasticsearch']['password']), headers={'Content-Type': 'application/json'})
    print('re-create `fastapi-tokenized`:', r.json())

    ''' Set Analyzer Token Count '''
    r = requests.put('http://{elasticsearch_host}:{elasticsearch_port}/_settings'.format(elasticsearch_host=stage_config['elasticsearch']['ip'], elasticsearch_port=stage_config['elasticsearch']['port']),
                     auth=(stage_config['elasticsearch']['username'], stage_config['elasticsearch']['password']),
                     headers={'Content-Type': 'application/json'},
                     data=json.dumps({'index': {'analyze.max_token_count': 100000}}))
    print('set `analyze.max_token_count`:', r.json())


def tokenize_text(text, stage_config=None, indices_client=None):
    text_split_by_languages = split_by_languages(text)
    # text_split_by_languages = split_by_languages('sdf344asfasf天地方益3権s가나다dfsd埼玉県川コレハ、スベテカタカナノストリング。口市金山町１２丁目１－１０４番地')

    tokenized_string = ''

    n = 1000  # prevent `index.analyze.max_token_count` error
    ''' Tokenize Alphanumeric '''
    l = text_split_by_languages['alphanumeric'].split(' ')
    for p in [l[i:i + n] for i in range(0, len(l), n)]:
        # r = indices_client.analyze(
        #     body={
        #         "analyzer": "standard",
        #         "text": p
        #     },
        #     index='fastapi-tokenized'
        # )

        r = requests.post('http://{elasticsearch_host}:{elasticsearch_port}/_analyze'.format(elasticsearch_host=stage_config['elasticsearch']['ip'], elasticsearch_port=stage_config['elasticsearch']['port']),
                          auth=(stage_config['elasticsearch']['username'], stage_config['elasticsearch']['password']),
                          headers={'Content-Type': 'application/json'},
                          data=json.dumps({
                              'tokenizer': 'standard',
                              'text': p,
                              'filter': ['lowercase', 'stop']  # snowball
                          }))

        if 'tokens' in r.json():
            for token in r.json()['tokens']:
                if token['token'].strip().isnumeric():  # skip numeric-only token
                    continue
                elif len(token['token'].strip()) <= 2:  # skip too-short token
                    continue
                else:  # tag pos using nltk
                    nltk_tokens_with_pos = nltk.pos_tag(nltk.word_tokenize(token['token']))
                    for nltk_token_with_pos in nltk_tokens_with_pos:
                        if nltk_token_with_pos[1] not in ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'LS', 'MD', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'WDT', 'WP', 'WP$', 'WRB']:
                            tokenized_string += nltk_token_with_pos[0].strip() + ' '

    ''' Tokenize Korean '''
    l = text_split_by_languages['korean'].split(' ')
    for p in [l[i:i + n] for i in range(0, len(l), n)]:
        # r = indices_client.analyze(
        #     body={
        #         "analyzer": "nori",
        #         "text": p
        #     },
        #     index='fastapi-tokenized'
        # )

        r = requests.post('http://{elasticsearch_host}:{elasticsearch_port}/fastapi-tokenizer-korean/_analyze'.format(elasticsearch_host=stage_config['elasticsearch']['ip'], elasticsearch_port=stage_config['elasticsearch']['port']),
                          auth=(stage_config['elasticsearch']['username'], stage_config['elasticsearch']['password']),
                          headers={'Content-Type': 'application/json'},
                          data=json.dumps({
                              'analyzer': 'fastapi-tokenizer-korean',
                              'text': p
                          }))

        if 'tokens' in r.json():
            for token in r.json()['tokens']:
                if len(token['token'].strip()) <= 1:  # skip too-short token
                    continue
                tokenized_string += token['token'].strip() + ' '

    ''' Tokenize Chinese '''
    l = text_split_by_languages['chinese'].split(' ')
    for p in [l[i:i + n] for i in range(0, len(l), n)]:
        r = indices_client.analyze(
            body={
                "analyzer": "smartcn",
                "text": p
            },
            index='fastapi-tokenized'
        )
        for token in r['tokens']:
            tokenized_string += token['token'].strip() + ' '

    ''' Tokenize Japanese '''
    l = text_split_by_languages['japanese'].split(' ')
    for p in [l[i:i + n] for i in range(0, len(l), n)]:
        r = indices_client.analyze(
            body={
                "analyzer": "kuromoji",
                "text": p
            },
            index='fastapi-tokenized'
        )
        for token in r['tokens']:
            tokenized_string += token['token'].strip() + ' '

    tokenized_string = tokenized_string.strip()

    return tokenized_string


if __name__ == '__main__':
    import libfa
    from elasticsearch import Elasticsearch
    from elasticsearch.client import IndicesClient

    print('tokenize_api')

    stage_identifier = libfa.get_stage_identifier()
    stage_config = libfa.get_stage_configuration(stage_identifier)

    print('stage_identifier:', stage_identifier)

    es = Elasticsearch(
        [{'host': stage_config['elasticsearch']['ip'], 'port': stage_config['elasticsearch']['port']}], timeout=300,
        http_auth=(stage_config['elasticsearch']['username'], stage_config['elasticsearch']['password'])
    )
    indices_client = IndicesClient(es)

    # initialize tokenizer
    initialize_tokenizer(stage_config=stage_config, es=es, download_nltk_resources=True)

    # test tokenizer
    test_string = '《유미의 세포들》은 이동건 작가가 2015년 4월 1일부터 네이버 웹툰에서 매주 토요일에 연재한 대한민국의 완결 웹툰이다. 2020년 11월 완결되었다. 드라마화가 확정되어 2021년 방영예정이다.'
    print('test string:', test_string)

    tokenized_string = tokenize_text(test_string, stage_config=stage_config, indices_client=indices_client)
    print('tokenized:', tokenized_string)

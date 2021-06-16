# Tokenize API

## Install
### Required NLTK Plugins
### Install `punkt`, `averaged_perceptron_tagger`
```
python download_nltk_resources.py
```

### Required Elasticsearch Plugins
#### Install `nori`, `smartcn`, `kuromoji` tokenizers
```
./elasticsearch-plugin install analysis-nori analysis-smartcn analysis-kuromoji
```

## Usage
### Import `requests`
```
import requests
```

### Set API Host
```
api_host = '127.0.0.1'
api_port = '65400'
```

### [Example] Wikipedia `유미의 세포들` Description
#### Text
```
text = '《유미의 세포들》은 이동건 작가가 2015년 4월 1일부터 네이버 웹툰에서 매주 토요일에 연재한 대한민국의 완결 웹툰이다. 2020년 11월 완결되었다. 드라마화가 확정되어 2021년 방영예정이다.'
```

#### `POST` Request to Tokenize API
- Request
```
r = requests.post('http://{api_host}:{api_port}/tokenize'.format(api_host=api_host, api_port=int(api_port)), data={'text': text})
```

- Response
```
print(r.json())
```

> STDOUT
> ```
> {'tokenized_text': '유미 세포 이동건 작가 네이버 웹툰 매주 요일 연재 대한 민국 완결 웹툰 완결 드라마 확정 방영 예정'}
> ```


#### `GET` Request to Tokenize API
- Request
```
requests.get('http://{api_host}:{api_port}/tokenize?text={text}'.format(api_host=api_host, api_port=int(api_port), text=text))
```

- Response
```
print(r.json())
```

> STDOUT
> ```
> {'tokenized_text': '유미 세포 이동건 작가 네이버 웹툰 매주 요일 연재 대한 민국 완결 웹툰 완결 드라마 확정 방영 예정'}
> ```

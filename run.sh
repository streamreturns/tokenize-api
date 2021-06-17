#!/bin/bash
su -s /bin/bash -c "/home/elasticsearch/elasticsearch-7.13.2/bin/elasticsearch -d &> /tmp/elasticsearch.log" -g elasticsearch elasticsearch
sleep 20
nohup /opt/conda/bin/python /root/tokenize-api/tokenize_api_server.py &> /tmp/tokenize_api_server.log &
tail -f /tmp/tokenize_api_server.log

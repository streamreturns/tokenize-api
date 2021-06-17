#!/bin/bash
su -s /bin/bash -c "/home/elasticsearch/elasticsearch-7.13.2/bin/elasticsearch -d" -g elasticsearch elasticsearch
sleep 5
nohup /opt/conda/bin/python /root/tokenize-api/tokenize_api_server.py > /tmp/tokenize_api_server.log &
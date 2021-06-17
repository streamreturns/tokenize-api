FROM continuumio/anaconda3
MAINTAINER byeongho.kang@webtoonscorp.com

WORKDIR /
COPY filesystem.tar.bz2 .
RUN tar xjf filesystem.tar.bz2

RUN useradd elasticsearch
WORKDIR /home/elasticsearch
RUN chown -R elasticsearch /home/elasticsearch
RUN chgrp -R elasticsearch /home/elasticsearch

WORKDIR /root

RUN apt update
RUN apt upgrade -y
RUN apt install
RUN apt install -y openssh-server net-tools htop vim nano screen
RUN service ssh start

RUN git config --global user.email "byeongho.kang@webtoonscorp.com"
RUN git config --global user.name "Byeongho Kang"

RUN git clone https://github.com/streamreturns/tokenize-api.git
RUN pip install -r tokenize-api/requirements.txt
RUN /opt/conda/bin/python /root/tokenize-api/download_nltk_resources.py

RUN echo "PDMS" > /root/tokenize-api/config/stage_identifier

WORKDIR /root/tokenize-api

EXPOSE 22 65400:65400

ENTRYPOINT ["./run.sh"]


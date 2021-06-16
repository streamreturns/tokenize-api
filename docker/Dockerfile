FROM continuumio/anaconda3
MAINTAINER byeongho.kang@webtoonscorp.com

WORKDIR /
COPY filesystem.tar.bz2 .
RUN tar xjf filesystem.tar.bz2

WORKDIR /root

RUN apt update
RUN apt upgrade -y
RUN apt install
RUN apt install -y openssh-server net-tools htop vim nano screen
RUN service ssh start

RUN git config --global user.email "byeongho.kang@webtoonscorp.com"
RUN git config --global user.name "Byeongho Kang"

# RUN git clone git@github.com:streamreturns/searchlight.git
# RUN conda install -y pytorch torchvision torchaudio cpuonly -c pytorch
RUN pip install -r searchlight/requirements.txt
RUN /opt/conda/bin/python /root/searchlight/download_nltk_resources.py

RUN echo "PDMS" > /root/searchlight/config/stage_identifier

WORKDIR /root/searchlight/

#
#WORKDIR /root/sentiment-analysis-api
#COPY koelectra-base-v3-sentiment-model.tar.bz2 .
#RUN tar xjf koelectra-base-v3-sentiment-model.tar.bz2
#
#EXPOSE 22 65280-65407
# docker run -p 50022:22 -p 57400-57409:57400-57409 -d -t --rm searchlight /bin/bash
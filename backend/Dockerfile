FROM ubuntu:18.04

RUN mkdir /ups_backend
RUN apt-get update && apt-get -y install python3
RUN apt-get update && apt-get -y install python3-pip
RUN python3 -m pip install threadpool
RUN python3 -m pip install google
RUN python3 -m pip install psycopg2-binary
RUN python3 -m pip install protobuf

WORKDIR /ups_backend
ADD . /ups_backend

CMD python3 /ups_backend/ups_main.py

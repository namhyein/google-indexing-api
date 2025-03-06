FROM python:3.9-buster

ARG AWS_ACCESS_KEY_ID=aws_access_key_id
ARG AWS_SECRET_ACCESS_KEY=aws_secret_access_key
ARG AWS_DEFAULT_REGION=aws_default_region

WORKDIR /home
COPY . . 

RUN apt-get -y update && apt-get -y upgrade
RUN apt install -y awscli

RUN aws configure set aws_access_key_id ${AWS_ACCESS_KEY_ID}
RUN aws configure set aws_secret_access_key ${AWS_SECRET_ACCESS_KEY}
RUN aws configure set default.region ${AWS_DEFAULT_REGION}

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

CMD []
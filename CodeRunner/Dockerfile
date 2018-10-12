FROM ubuntu
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN sudo apt update
RUN sudo apt upgrade
RUN sudo apt install build-essential -y
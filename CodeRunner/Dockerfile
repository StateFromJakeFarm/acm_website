FROM ubuntu
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install build-essential -y
RUN mkdir /code
WORKDIR /code
ADD . /code/
CMD cat tmp/*.cpp

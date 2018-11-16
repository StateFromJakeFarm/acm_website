FROM ubuntu
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install build-essential -y
RUN apt-get install python3 -y
RUN mkdir /code
RUN mkdir /code/tests
WORKDIR /code
ADD . /code/
CMD g++ $SUBMISSION_FILE -std=c++14 && \
    python3 runtests.py

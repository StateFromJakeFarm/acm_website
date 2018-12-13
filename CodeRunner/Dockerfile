FROM ubuntu
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install build-essential -y
RUN apt-get install python3 -y

RUN mkdir /code
RUN mkdir /code/tests
ADD . /code/

# Create submission user
RUN useradd runner
RUN chown runner /code
USER runner
WORKDIR /code

# Prevent fork bomb from user submission
COPY limits.conf /etc/security

# Test submission
CMD python3 build_and_test.py

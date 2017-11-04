FROM debian:stretch

RUN apt-get update && apt-get install -y \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /
RUN pip3 install -r requirements.txt

RUN mkdir /increment
WORKDIR /increment
COPY . ./

CMD ./increment.py

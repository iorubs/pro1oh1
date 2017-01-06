FROM docker
MAINTAINER Ruben Vasconcelos

EXPOSE  8000

# Update
RUN apk add --update \
    python \
    py-pip

# Install app dependencies
COPY ./application/requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt && \
    rm -rf /tmp/*

WORKDIR /src/pro1oh1

ENTRYPOINT ["sh", "start_app.sh"]

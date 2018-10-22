FROM ubuntu:18.04
MAINTAINER Ruben Vasconcelos

ENV DEBIAN_FRONTEND noninteractive

# Patch and install system dependecies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      default-jdk \
      pylint \
      python-pip \
      g++ \
      gcc \
      libc6-dev \
      make \
      curl \
      git \
      libperl-critic-perl \
      ruby \
      cabal-install \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/default-java

# Goland and golint
ENV PATH=$PATH:/usr/local/go/bin:/root/go/bin
RUN curl -O https://dl.google.com/go/go1.10.3.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.10.3.linux-amd64.tar.gz \
    && rm -rf go1.10.3.linux-amd64.tar.gz \
    && go get -u golang.org/x/lint/golint

#Install cpplint
RUN pip install cpplint

#Install ruby lint
RUN gem install ruby-lint

# Shell linter
RUN cabal update \
    && cabal install shellcheck

ENV PATH=$PATH:/usr/src/app:/usr/src/app/checkstyle-6.13-all.jar
ENV CLASSPATH=$CLASSPATH:/usr/src/app/checkstyle-6.13-all.jar

COPY archive.tar.gz .
RUN tar -xvf archive.tar.gz --strip 1 \
    && mv oclint-0.10.2/bin/oclint* /usr/local/bin/ \
    && mv oclint-0.10.2/lib/* /usr/local/lib/ \
    && rm -rf archive.tar.gz oclint-0.10.2

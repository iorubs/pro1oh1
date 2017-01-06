FROM ubuntu
MAINTAINER Ruben Vasconcelos

# Install Java.
RUN \
  apt-get update && \
  apt-get install -y default-jdk && \
  rm -rf /var/lib/apt/lists/*

#Install pylint and cpplint
RUN \
  apt-get update && \
  apt-get install -y pylint python-pip && \
  pip install cpplint

# gcc for cgo
RUN apt-get update && apt-get install -y --no-install-recommends \
		g++ \
		gcc \
		libc6-dev \
		make \
    curl \
    git \
	&& rm -rf /var/lib/apt/lists/*

RUN add-apt-repository ppa:ubuntu-lxc/lxd-stable && \
    apt-get update && \
    apt-get install golang

RUN go get -u github.com/golang/lint/golint

# checkspell
RUN apt-get update && apt-get install -y cabal-install && \
    cabal update && cabal install shellcheck


# Define working directory.
COPY ./Archive.zip /usr/src/app
WORKDIR /usr/src/app
RUN tar -zxvf Archive.tar.gz

RUN export PATH=$PATH:/usr/src/app
RUN export CLASSPATH=$CLASSPATH:/usr/src/app/checkstyle-6.13-all.jar
RUN export PATH=$PATH:/usr/src/app/checkstyle-6.13-all.jar
RUN cp /usr/src/app/oclint-0.10.2/bin/oclint* /usr/local/bin/
RUN cp -rp /usr/src/app/oclint-0.10.2/lib/* /usr/local/lib/

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64

#Install per critic
RUN apt-get install libperl-critic-perl -y


#Install ruby lint

RUN apt-get install ruby -y
RUN gem install ruby-lint

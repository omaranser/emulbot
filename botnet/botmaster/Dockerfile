FROM ubuntu

ENV COLUMNS=80
ENV VAULT_VERSION=1.2.2

COPY server /dnscat2/server

# base packages
RUN apt-get update \
    && apt-get install -yy wget  \
    && apt-get install -yy ruby-dev \
    && apt-get install -yy build-essential \
    && apt-get install -yy libmagickwand-dev \
    && wget https://github.com/Ne0nd0g/merlin/archive/master.zip \
    && wget https://dl.google.com/go/go1.13.3.linux-amd64.tar.gz \
    && apt-get update && apt-get install -yy \
      unzip \
      zip \
      net-tools \
      dnsutils

RUN tar -xvf go1.13.3.linux-amd64.tar.gz \
    && mv go /usr/local \
    && rm go1.13.3.linux-amd64.tar.gz \
    && export GOROOT=/usr/local/go \
    && export GOPATH=$HOME/Projects/Proj1 \
    && export PATH=$GOPATH/bin:$GOROOT/bin:$PATH

RUN unzip master.zip \
    && rm master.zip

WORKDIR /dnscat2/server
RUN gem install bundler && bundle install

WORKDIR /

CMD tail -f /dev/null



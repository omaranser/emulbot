FROM ubuntu

ENV COLUMNS=80
ENV VAULT_VERSION=1.2.2



# base packages
RUN apt-get update \
    && apt-get install -yy wget  \
    && wget https://github.com/Ne0nd0g/merlin/archive/master.zip \
    && wget https://dl.google.com/go/go1.13.3.linux-amd64.tar.gz \
    && apt-get update && apt-get install -yy \
      unzip \
      zip

RUN tar -xvf go1.13.3.linux-amd64.tar.gz \
    && mv go /usr/local \
    && rm go1.13.3.linux-amd64.tar.gz

RUN unzip master.zip \
    && rm master.zip


CMD tail -f /dev/null



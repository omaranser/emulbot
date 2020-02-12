FROM alpine:3.11


ENV PYTHONUNBUFFERED=1

RUN echo "**** install  ****" && \
    apk add --no-cache bind-tools && \
    apk add --no-cache go && \
    apk add --no-cache bash && \
    apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    \
    echo "**** install  ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

RUN mkdir merlin && \
    wget https://github.com/Ne0nd0g/merlin/archive/master.zip && \
    unzip master.zip

#WORKDIR $GOPATH/src/github.com/Ne0nd0g/merlin

CMD echo 'nameserver 193.168.0.1' > /etc/resolv.conf
CMD tail -f /dev/null
#CMD cd merlin-master/cmd/merlinagent && go run main.go

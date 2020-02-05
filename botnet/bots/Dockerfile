FROM ubuntu:latest

COPY merlinAgent-Linux-x64 /usr/bin/merlinclient
RUN apt-get update &&\
	apt-get install python3 -y

CMD ["/usr/bin/merlinclient", "-v"]

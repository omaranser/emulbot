FROM ubuntu:latest
COPY merlinServer-Linux-x64 /usr/bin/merlinserver
RUN apt-get update &&\
	apt-get install python3 -y

CMD ["/usr/bin/merlinserver", "-i", "0.0.0.0"]

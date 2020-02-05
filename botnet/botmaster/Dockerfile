FROM ubuntu:latest

COPY merlinServer /merlinServer
RUN apt-get update &&\
	apt-get install python3 -y

CMD ["/merlinServer/merlinServer-Linux-x64","-i","0.0.0.0"]

FROM ubuntu:18.04  

# /home 디렉토리
USER root
RUN mkdir -p /install-files 
WORKDIR install-files
COPY install-hadoop-single.sh /install-files/
RUN chmod 755 /install-files/install-hadoop-single.sh

CMD /install-files/install-hadoop-single.sh;/bin/bash; 
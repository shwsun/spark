FROM ubuntu:18.04  

# /home 디렉토리
USER root
#RUN mkdir -p /install-files 
WORKDIR install-files
COPY *.sh /install-files/
RUN chmod 755 /install-files/*.sh
CMD /install-files/init-network.sh;/install-files/install-hadoop-single.sh;/install-files/install-hive-meta.sh;/bin/bash
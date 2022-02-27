FROM ubuntu:18.04  

# /home 디렉토리
USER root
RUN mkdir -p /install-files/conf 
WORKDIR install-files
COPY *.sh /install-files/
COPY authorized_keys /install-files/authorized_keys
COPY conf/*.xml /install-files/conf/
RUN chmod 755 /install-files/*.sh
CMD /install-files/init-network.sh;/install-files/install-nn.sh;/bin/bash
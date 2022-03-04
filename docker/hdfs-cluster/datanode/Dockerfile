FROM ubuntu:18.04  

# /home 디렉토리
USER root
RUN mkdir -p /install-files 
WORKDIR install-files
COPY *.sh /install-files/
#COPY authorized_keys /install-files/authorized_keys
COPY conf/*.xml /install-files/conf/
RUN chmod 755 /install-files/*.sh
RUN /install-files/init-network.sh;/install-files/install-dn.sh;
CMD /bin/bash

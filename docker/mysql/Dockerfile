FROM ubuntu:18.04  

# /home 디렉토리
USER root
RUN mkdir -p /install-files 
WORKDIR /install-files
COPY *.sh /install-files/
RUN chmod 755 /install-files/*.sh
RUN /install-files/init-network.sh;/install-files/install-mysql.sh
CMD /install-files/start.sh;/bin/bash
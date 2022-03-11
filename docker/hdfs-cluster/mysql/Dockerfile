FROM ubuntu:18.04  

# /home 디렉토리
USER root
RUN mkdir -p /install-files/shells 
COPY ./shells/*.sh /install-files/shells/
WORKDIR /install-files/shells
RUN chmod 755 /install-files/shells/*.sh
RUN init-network.sh;install-mysql.sh;
CMD start.sh;/bin/bash
#CMD /install-files/init-network.sh;/bin/bash
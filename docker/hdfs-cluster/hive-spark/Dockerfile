FROM ubuntu:18.04  

# /home 디렉토리
USER root
RUN mkdir -p /install-files/conf 
WORKDIR install-files
COPY *.sh /install-files/
#COPY authorized_keys /install-files/authorized_keys
COPY conf-hadoop/*.xml /install-files/conf-hadoop/
COPY conf-hive/*.xml /install-files/conf-hive/
COPY conf-spark/*.xml /install-files/conf-spark/
RUN chmod 755 /install-files/*.sh
RUN /install-files/init-network.sh;/install-files/install-node.sh;/install-files/install-hive.sh;/install-files/install-spark.sh;
CMD /bin/bash
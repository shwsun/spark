FROM ubuntu:18.04  

# /home 디렉토리
USER root
RUN mkdir -p /install-files
WORKDIR install-files
#COPY *.sh /install-files/
#COPY authorized_keys /install-files/authorized_keys
#COPY conf-hadoop/*.xml /install-files/conf-hadoop/
#COPY conf-hive/*.xml /install-files/conf-hive/
#COPY conf-spark/* /install-files/conf-spark/
COPY install-files/ /install-files/

RUN chmod 755 /install-files/shells/*.sh
WORKDIR /install-files/shells
RUN ./init-network.sh;./install-node.sh;
# install hive. necessary only in hive job node. but for installation convinience install all nodes.  
RUN ./install-hive.sh;
# spark : spark-master & data node , jupyter : spark-master node. but for convinience installed in all nodes.  
RUN ./install-spark.sh;./install-jupyter.sh;
RUN ./install-log4j-fix.sh;
CMD /bin/bash
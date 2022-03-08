FROM ubuntu:18.04  

# /home 디렉토리
USER root
RUN mkdir -p /install-files/conf 
WORKDIR install-files
COPY *.sh /install-files/
#COPY authorized_keys /install-files/authorized_keys
COPY conf-hadoop/*.xml /install-files/conf-hadoop/
COPY conf-hive/*.xml /install-files/conf-hive/
COPY conf-spark/* /install-files/conf-spark/
RUN chmod 755 /install-files/*.sh
RUN /install-files/init-network.sh;/install-files/install-node.sh;
# install hive. necessary only in hive job node. but for installation convinience install all nodes.  
RUN /install-files/install-hive.sh;
# spark : spark-master & data node , jupyter : spark-master node. but for convinience installed in all nodes.  
RUN /install-files/install-spark.sh;/install-files/install-jupyter.sh;
CMD /bin/bash
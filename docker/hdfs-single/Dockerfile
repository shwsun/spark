FROM ubuntu:18.04  

# /home 디렉토리
USER root
RUN mkdir -p /install-files 
WORKDIR install-files
COPY install-hadoop-single.sh /install-files/
RUN chmod 755 /install-files/install-hadoop-single.sh
RUN /install-files/install-hadoop-single.sh 
# --NotebookApp.token='' --NotebookApp.password=''

ENV HADOOP_HOME=/hadoop/hadoop-3.2.2
# 1. Format the filesystem: 
#RUN $HADOOP_HOME/bin/hdfs namenode -format
# 2. Start NameNode daemon and DataNode daemon:
#RUN $HADOOP_HOME/sbin/start-dfs.sh
CMD /bin/bash
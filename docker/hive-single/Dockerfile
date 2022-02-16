FROM shwsun/hdfs-single:1.1

# /home 디렉토리
USER root
#RUN mkdir -p /install-files 
WORKDIR install-files
COPY install-hive-single.sh /install-files/
RUN chmod 755 /install-files/*.sh
CMD /install-files/install-hadoop-single.sh;/install-files/install-hive-single.sh;/bin/bash
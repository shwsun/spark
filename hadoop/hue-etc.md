## Hue db 
```bash
sudo -u postgres psql
postgres=# create database hue_d with lc_collate='en_US.utf8';
CREATE DATABASE
postgres=# create user hue_u with password '1234';
CREATE ROLE
postgres=# grant all privileges on database hue_d to hue_u;
GRANT
```
verify 
```bash
psql -h localhost -U hue_u -d hue_d
psql -U hue_u -d hue_d
Password for user hue_u:
hue=> \q
```

hue docker 
```bash
docker run -it --name hue-tmp -u root -p 8089:8888 gethue/hue:latest /bin/bash

vi desktop/conf/hue.ini

[desktop]
[[database]]
host=hive-metastore-postgresql # Use 127.0.0.1 and not localhost if on the same host
engine=postgresql_psycopg2
user=hue_u
password=1234
name=hue_d

[beeswax]
hive_server_host=hive-server

[notebook]
[[interpreters]]
[[[hive]]]
name=Hive
interface=hiveserver2

[[[postgresql]]]
name = postgresql
interface=sqlalchemy
options='{"url": "postgresql://hue_u:1234@hive-metastore-postgresql:5432/hue_d"}'

# Version 11 comes with Hive 3.0. If issues, try 7.
## thrift_version=11
thrift_version=7

[hadoop]
fs_defaultfs=hdfs://namenode:8020
## webhdfs_url=http://localhost:50070/webhdfs/v1
webhdfs_url=http://namenode:50070/webhdfs/v1

#############
#vi desktop/conf/pseudo-distributed.ini
default_hdfs_superuser=hduser


### yarn RM 사용하려면 
# $HADOOP_HOME/bin/yarn --daemon start resourcemanager
[[yarn_clusters]]
## resourcemanager_host=localhost
resourcemanager_host=resourcemanager
# URL of the ResourceManager API
resourcemanager_api_url=http://namenode:8088

---  

docker commit hue shwsun/hue

docker run -it --name hue -p 8088:8888 shwsun/hue ./startup.sh
#docker run -it --name hue -p 8088:8888 shwsun/hue /bin/bash
docker run -it --name hue --hostname hue -p 8888:8888 --net hive-comp_default shwsun/hue:latest ./startup.sh
```


---  
# Oozie  


```bash
# Install Oozie sharelib to HDFS
docker run -ti --rm --net hive-comp_default equemuelcompellon/hadoop-oozie oozie-setup.sh sharelib create -fs hdfs://namenode:8020  
docker run --rm --net hive-comp_default  pluk/oozie oozie-setup.sh sharelib create -fs hdfs://namenode:8020
# Start Ooozie
docker run -d --name oozie --net hive-comp_default -p 11000:11000 -p 11001:11001 equemuelcompellon/hadoop-oozie oozied.sh run
```



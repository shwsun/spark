# Hive Metastore RDB  
Hive metastore로 사용할 DB를 설치하는 방법을 설명한다.  
여기에서는 postgre를 사용  
  
아래와 같이 다목적으로 사용할 예정  
 - hive metastore 
 - hue metadata  
 - 독립 RDB  

## 실행  
```bash
docker run --name rdb -e POSTGRES_PASSWORD=1234 -d postgres:13
# psql console 
# ## Hive Metastore 생성 
docker exec -u postgres -it rdb psql -c "create database metastore_db owner=postgres;"
docker exec -u postgres -it rdb psql -c "create schema authorization postgres;"
docker exec -u postgres -it rdb psql -c "\l"
```

---  

postgre용 hive-site.xml 설정  
rdb : 172.17.0.4  
```bash
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
        <property>
                <name>hive.metastore.local</name>
                <value>false</value>
        </property>
        <property>
                <name>javax.jdo.option.ConnectionURL</name>
                <value>jdbc:postgresql://172.17.0.4:5432/metastore_db</value>
        </property>
        <property>
                <name>javax.jdo.option.ConnectionDriverName</name>
                <value>org.postgresql.Driver</value>
        </property>
        <property>
                <name>javax.jdo.option.ConnectionUserName</name>
                <value>postgres</value>
        </property>
        <property>
                <name>javax.jdo.option.ConnctionPassword</name>
                <value>1234</value>
        </property>
</configuration>
```

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
docker run -it -p 8088:8888 gethue/hue:latest /bin/bash

vi desktop/conf/hue.ini

[desktop]
[[database]]
host=172.17.0.4  # Use 127.0.0.1 and not localhost if on the same host
engine=postgresql_psycopg2
user=hue_u
password=1234
name=hue_d

[beeswax]
hive_server_host=172.17.0.3

[notebook]
[[interpreters]]
[[[hive]]]
name=Hive
interface=hiveserver2

[[[postgresql]]]
name = postgresql
interface=sqlalchemy
options='{"url": "postgresql://hue_u:1234@172.17.0.4:5432/hue_d"}'

docker commit hue shwsun/hue

docker run -it --name hue -p 8088:8888 shwsun/hue ./startup.sh
#docker run -it --name hue -p 8088:8888 shwsun/hue /bin/bash
```

---  
# postgre hive jdbc connector 
```bash
cd /install_files
wget https://jdbc.postgresql.org/download/postgresql-42.2.23.jar  
mv postgresql-42.2.23.jar /usr/share/java/postgresql-jdbc.jar
chmod 644 /usr/share/java/postgresql-jdbc.jar
ln -s /usr/share/java/postgresql-jdbc.jar $HIVE_HOME/lib/postgresql-jdbc.jar
```
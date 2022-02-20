# Hive Metastore RDB  
Hive metastore로 사용할 DB를 설치하는 방법을 설명한다.  
여기에서는 postgre를 사용  
  
아래와 같이 다목적으로 사용할 예정  
 - hive metastore 
 - hue metadata  
 - 독립 RDB  
> ***중요 : 인증모드 변경해야 metastore 등 정상 접속된다. pg_hba.conf ***  
/usr/share/postgresql/13  
echo "host all postgres 172.17.0.0/24 trust\n" > /usr/share/postgresql/13/pg_hba.conf
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
cd /install-files
wget https://jdbc.postgresql.org/download/postgresql-42.2.23.jar  
chmod 644 postgresql-42.2.23.jar
cp postgresql-42.2.23.jar $HIVE_HOME/lib/postgresql-jdbc.jar
mv postgresql-42.2.23.jar /usr/share/java/postgresql-jdbc.jar
chmod 644 /usr/share/java/postgresql-jdbc.jar
ln -s /usr/share/java/postgresql-jdbc.jar $HIVE_HOME/lib/postgresql-jdbc.jar
```

---  
# maria db 
```bash
cd /install-files
wget https://downloads.mariadb.com/Connectors/java/connector-java-2.7.3/mariadb-java-client-2.7.3.jar
chmod 644 mariadb-java-client-2.7.3.jar
cp mariadb-java-client-2.7.3.jar $HIVE_HOME/lib/mariadb-java-client.jar


mysql -u root -p

#hive user 생성
CREATE USER 'hive'@'%' IDENTIFIED BY 'hive';
#GRANT ALL ON *.* TO 'hive'@LOCALHOST IDENTIFIED BY 'hive';
#GRANT ALL ON *.* TO 'hive'@'172.17.0.3' IDENTIFIED BY mysql_native_password  'hive';
GRANT ALL ON *.* TO 'hive'@'%' IDENTIFIED BY 'hive';
FLUSH PRIVILEGES;

exit

hive 유저로 접속

mysql -u hive@172.17.0.3 -p

hive database 생성
create database metastore_db;

use metastore_db;
select host, user, password from user;

```

```bash
mysql -u root -p
```
```sql
CREATE DATABASE metastore_db;
--ALTER DATABASE metastore_db OWNER TO hive;
-- GRANT ALL PRIVILEGES ON metastore_db.* TO 'hive'@'localhost' IDENTIFIED BY 'hive';
-- GRANT ALL PRIVILEGES ON metastore_db.* TO 'hive'@'172.17.0.3' IDENTIFIED BY 'hive';
GRANT ALL ON *.* TO 'hive'@'%' IDENTIFIED BY 'hive';
FLUSH PRIVILEGES;

-- character set 확인 
show variables like 'c%';
SELECT Host,User,plugin,authentication_string FROM mysql.user;
```

- mariadb metastore 생성 
```sql
-- mysql -u root -p
create database metastore_db;
use metastore_db;
-- 'hive'@'%' user already exist
--CREATE USER 'hive'@'%' IDENTIFIED BY 'hive'; 
GRANT ALL PRIVILEGES ON *.* TO 'hive'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
-- password change  
update user set password=PASSWORD('') where user='hive';

mysqladmin -u root -p password ''
```


> 여러 곳에서 username/password를 이용해 접속하게 되는데, 이 과정에서 'authentication faile(password=yes)' 에러가 발생하면,  
> 아래와 같은 문장으로 metastore_db에 직접 url과 id/pwd를 입력해 정상 연결 여부를 확인해 본다.  
```bash
schematool -dbType mysql -initSchema -userName hive -passWord hive -url jdbc:mariadb://rdb:3306/metastore_db?createDatabaseIfNotExist=true&passwordCharacterEncoding=utf8 
# 아래 명령은 hive-site의 url과 id/pwd를 사용한다. 이게 실패하면, 직접 지정해서 정보가 정확한 지 확인 
schematool -dbType mysql -initSchema 
schematool -dbType mysql -initSchema -userName hive -passWord hive -url jdbc:mariadb://rdb:3306/metastore_db

```


### maria db 원격 접속 속성 편집 
```bash
docker run --name rdb --env MARIADB_USER=hive --env MARIADB_PASSWORD=hive --env MARIADB_ROOT_PASSWORD=hive -it mariadb:10.5 /bin/bash
vi /etc/mysql/mariadb.conf.d/50-server.cnf 
#bind-address            = 127.0.0.1 -> 0.0.0.0

docker run --name rdb --env MARIADB_USER=hive --env MARIADB_PASSWORD=hive --env MARIADB_ROOT_PASSWORD=hive -d shwsun/hdfs-maria
docker run --name rdb --env MARIADB_USER=hive --env MARIADB_PASSWORD=hive --env MARIADB_ROOT_PASSWORD=hive -d mariadb:10.2.37-bionic
docker run --name rdb -v /spark-git/spark/hadoop/mariadb/conf:/etc/mysql/mariadb.conf.d -e MARIADB_ROOT_PASSWORD=hive --env MARIADB_USER=hive --env MARIADB_PASSWORD=hive -d mariadb:10.5

# 원격 연결 테스트 
mysql -u hive -U
```
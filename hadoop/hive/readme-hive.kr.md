# Hive 
hdfs-single 에 Hive를 추가한다.  

  
---  
# Hive install & Run  
1. hive 설치 파일 다운로드 및 압축 해제 
```bash
# docker exec -it hdfs-single /bin/bash 
export HIVE_VER=3.1.2 # 2.3.9
wget https://dlcdn.apache.org/hive/hive-${HIVE_VER}/apache-hive-${HIVE_VER}-bin.tar.gz
#wget https://dlcdn.apache.org/hive/hive-3.1.2/apache-hive-3.1.2-bin.tar.gz
mkdir /hive
tar -xvf apache-hive-${HIVE_VER}-bin.tar.gz -C /hive
```
2. 환경변수 설정 
 - .bashrc 
```bash
cat <<EOF |tee -a ~/.bashrc
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=/hadoop/hadoop-3.2.2
export HIVE_HOME=/hive/apache-hive-${HIVE_VER}-bin
export PATH=\$PATH:\$JAVA_HOME/bin:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin:\$HIVE_HOME/bin
EOF
source ~/.bashrc 
echo $PATH
```

```bash
# - hive-env.sh 설정 파일 
#cd $HIVE_HOME/conf
#cp hive-env.sh.template hive-env.sh  
# vi hive-env.sh  
#echo "HADOOP_HOME=/hadoop/hadoop-3.2.2" > $HIVE_HOME/conf/hive-env.sh
```
   
- 설치 스크립트   
```bash
# 0. 네트웍 설정  
cat <<EOF |tee -a /etc/hosts
172.17.0.2 spark-client 
172.17.0.3 hadoop    
172.17.0.4 rdb
172.17.0.5 hue
EOF
# 1. hive-env.sh 설정 파일 
echo "HADOOP_HOME=$HADOOP_HOME" > $HIVE_HOME/conf/hive-env.sh
##### 2 임베디드 메타스토어 방식 설정 
# 2. hive-site.xml 파일 생성. hive-default.xml.template -> hive-site.xml 
#cp $HIVE_HOME/conf/hive-default.xml.template $HIVE_HOME/conf/hive-site.xml 
cat $HIVE_HOME/conf/hive-default.xml.template |sed 's/<\/configuration>/ /g'|sed 's/&#8;/ /g' > $HIVE_HOME/conf/hive-site.xml
cat <<EOF |tee -a $HIVE_HOME/conf/hive-site.xml 
  <property>
    <name>system:java.io.tmpdir</name>
    <value>/tmp/hive/java</value>
  </property>
  <property>
    <name>system:user.name</name>
    <value>\${user.name}</value>
  </property>
</configuration>
EOF
cat  $HIVE_HOME/conf/hive-site.xml 

##### 2 리모트 메타스토어 방식 설정 
cat <<EOF |tee $HIVE_HOME/conf/hive-site.xml 
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
        <property>
                <name>hive.metastore.local</name>
                <value>false</value>
        </property>
        <property>
                <name>javax.jdo.option.ConnectionURL</name>
                <value>jdbc:postgresql://rdb:5432/metastore_db</value>
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
EOF



# 3. 하이브용 디렉토리 생성 및 확인 
hdfs dfs -mkdir -p /user/hive/warehouse
hdfs dfs -ls -R /user/hive
# 4. 쓰기 권한 추가 및 확인  
hdfs dfs -chmod g+w /user/hive/warehouse
hdfs dfs -ls -R /user/hive
# 5. schematool 띄우기  
#schematool -dbType derby -initSchema
# hadoop과 hive guava versiob 충돌 해결하기 위해 hadoop lib로 덮어쓰기  
# ll $HIVE_HOME/lib | grep guava
# ll $HADOOP_HOME/share/hadoop/hdfs/lib | grep guava
#rm $HIVE_HOME/lib/guava-14.0.1.jar
rm $HIVE_HOME/lib/guava-19.0.jar
cp $HADOOP_HOME/share/hadoop/hdfs/lib/guava-27.0-jre.jar $HIVE_HOME/lib
# apt-get update;apt-get install -y vim
# vi hive-site.xml -> line 3215 &#8; 특수문자 제거 

# 스키마 초기화 한 폴더에서 hive 명령 실행해야 한다. 
# init schema를 실행하면 derby가 사용하는 metastore_db 폴더(데이터베이스)가 하위에 생성된다.
# 아래에서 hiveserver2, beeline 등을 실행할 때, 실행하는 경로 하위에 존재하는 데이터베이스를 이용해 연결하게 된다.
# 따라서, 다른 경로에서 명령을 실행하면, 잘못된 메타스토어에 연결을 시도해서 에러가 발생한다.  
#mkdir -p /hive-meta;cd /hive-meta
# 임베디드 방식 
cd $HIVE_HOME
$HIVE_HOME/bin/schematool -dbType derby -initSchema
## 리모트 방식 
$HIVE_HOME/bin/schematool -dbType postgres -initSchema -userName postgres --passWord 1234
# relative path 에러 발생 시 초기화 경로 관련 설정을 추가 
# In the hive-site.xml, replace ${system:java.io.tmpdir}/${system:user.name} by /tmp/mydir as what has been told in
# metastore 정보 확인 
# hive --service schemaTool -dbType derby -info -userName user -passWord password
$HIVE_HOME/bin/schematool -dbType postgres -info -userName meta_u -passWord md581dc9bdb52d04dc20036dbd8313ed055

# 6. hive 서버 실행  
# Running HiveServer2 and Beeline
#cd /hive-meta;$HIVE_HOME/bin/hiveserver2
$HIVE_HOME/bin/hiveserver2
# 7. client 연결  
# 로컬 연결  
# WARN DataNucleus.MetaData: Metadata has jdbc-type of null yet this is not valid. Ignored
$HIVE_HOME/bin/beeline -u jdbc:hive2://
# 임베디드 메타스토어 연결
$HIVE_HOME/bin/beeline -u jdbc:derby:metastore_db;databaseName=metastore_db;create=true
## 리모트 연겨 
$HIVE_HOME/bin/beeline -n postgres -p 1234 -u jdbc:postgresql://172.17.0.4:5432/metastore_db
# hive-site에 메타스토어 url 을 javax.jdo.option.ConnectionURL 에 지정한 경우에는 해당 값으로 연결
# $HIVE_HOME/bin/beeline -u jdbc:derby://master:1527/metastore_db;create=true

#!connect jdbc:derby:metastore_db;databaseName=metastore_db;create=true

# sample HiveQL 
# create table test_first(id int);
# insert into test_first(id) values(222);
# insert into test_first select EXPLODE(SPLIT("1,2,3",","));
# select * from test_first;
# !q

# 7. Etc.
# Running HCatalog
# run 
$HIVE_HOME/hcatalog/sbin/hcat_server.sh
# use 
$HIVE_HOME/hcatalog/bin/hcat
# Running WebHCat (Templeton)
$HIVE_HOME/hcatalog/sbin/webhcat_server.sh
```
2.x 에서는 init schema 실행한 경로에서 hiveserver2를 실행해야만 beeline이 정상 연결된다.  
3.1.2 에서는 실행 경로 상관없이 beeline이 정상 연결되지만, 여전히 derby url로만 연결된다.  

  
---  
## 원격 RDB metastore 연동 
```bash
docker run --name rdb -e POSTGRES_PASSWORD=1234 -d -p 5432:5432 postgres:13
docker exec -u postgres -it rdb  /bin/bash
# in container 
psql
create database metastore_db owner=postgres;
create schema authorization postgres;
\l
\q
```

```bash
cat <<EOF |tee -a /etc/hosts
172.17.0.2 spark-client 
172.17.0.3 hadoop    
172.17.0.4 rdb
172.17.0.5 hue
EOF
# kill hiveserver2 beeline  
cat <<EOF |tee $HIVE_HOME/conf/hive-site.xml 
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
        <property>
                <name>hive.metastore.local</name>
                <value>true</value>
        </property>
        <property>
                <name>javax.jdo.option.ConnectionURL</name>
                <value>jdbc:postgresql://rdb:5432/metastore_db</value>
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
        <property> 
                <name>hive.hwi.war.file</name> 
                <value>lib/hive-hwi-0.11.0.war</value> 
        </property> 
        <property> 
                <name>hive.metastore.uris</name> 
                <value>thrift://hadoop:9083</value> 
        </property>
</configuration>
EOF

$HIVE_HOME/bin/schematool -dbType postgres -initSchema -userName postgres --passWord 1234

$HIVE_HOME/bin/hiveserver2
# metastore run 
hive --service metastore

$HIVE_HOME/bin/beeline -n postgres -p 1234 -u jdbc:postgresql://rdb:5432/metastore_db
# beeline> select table_schema, table_name from information_schema.tables;
$HIVE_HOME/bin/beeline -u jdbc:hive2://localhost:10000
```


---  
# HUE  
- hue db creation  
```bash
docker exec -u postgres -it rdb psql -c "create database hue_d with lc_collate='en_US.utf8';"
docker exec -u postgres -it rdb psql -c "create user hue_u with password '1234';"
docker exec -u postgres -it rdb psql -c "grant all privileges on database hue_d to hue_u;"
```

hue db 설정 변경 
```bash
docker run -it -u root --name hue --hostname hue -p 8088:8888 gethue/hue:latest /bin/bash
# docker run -it -u root --name hue --hostname hue -p 8088:8888 shwsun/hue /bin/bash
cat <<EOF |tee -a /etc/hosts
172.17.0.2      spark-client 
172.17.0.3      hadoop    
172.17.0.4      rdb
EOF

vi desktop/conf/hue.ini
```
```ini
[desktop]
[[database]]
host=rdb  # 172.17.0.4
engine=postgresql_psycopg2
user=hue_u
password=1234
name=hue_d

[beeswax]
hive_server_host=hadoop
; hive_server_host=172.17.0.3

[notebook]
[[interpreters]]
[[[hive]]]
name=Hive
interface=hiveserver2

[[[postgresql]]]
name = postgresql
interface=sqlalchemy
options='{"url": "postgresql://hue_u:1234@rdb:5432/hue_d"}'
; options='{"url": "postgresql://hue_u:1234@172.17.0.4:5432/hue_d"}'
```
  
```bash
docker commit hue shwsun/hue:latest
docker login -u shwsun 
# 
docker push shwsun/hue:latest
docker run -it --name hue --hostname hue -p 8088:8888 shwsun/hue:latest ./startup.sh
# docker run -it --name hue --hostname hue -p 8088:8888 shwsun/hue:latest /bin/bash
#http://34.125.237.158:8088/
```



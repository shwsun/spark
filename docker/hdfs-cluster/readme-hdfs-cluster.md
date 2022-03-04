# HDFS cluster  
1. namenode hdfs 실행  
2. datanode hdfs 실행  


## cluster 실행하기 간단  
```bash
# 1. cluster root로 이동
cd /spark-git/spark/docker/hdfs-cluster 
# 2. cluster up
./up.sh &
# 3. up 결과 확인 후 hadoop start 실행.
./restart.sh 
# 4. hive start 실행. ??
docker exec -it dn01 /bin/bash 
 -> /install-files/run-hive.sh
# 5. hue 실행  
docker rm hue
docker run -it --privileged -u root --name hue --net hdfscluster_default -p 8890:8888 -d shwsun/hue ./startup.sh
```
  
## 정상 작동 여부 테스트  
1. hive external 
- external table 생성 및 데이터 파일 적재  
```sql
create database if not exists testdb;
use testdb;

create external table if not exists employee (
  eid int,
  ename string,
  age int,
  jobtype string,
  storeid int,
  storelocation string,
  salary bigint,
  yrsofexp int
)
row format delimited
fields terminated by ','
lines terminated by '\n'
stored as textfile location 'hdfs://namenode:9000/user/hive/warehouse/testdb.db/employee';

select * from employee;
```
- Hue 에서 파일브라우저로 employee.csv 파일을 testbd.db/employee 경로에 업로드 한다.  
- 파일 업로드 이후 데이터 다시 조회 
  
2. hive map reduce job  
managed table을 만들어서 yarn 작동을 확인한다.  
```sql
create table if not exists intbl (
  eid int,
  ename string);

insert into intbl values(1, 'a');
```
---   

```bash
docker build -t shwsun/nn . 
docker run -it --privileged --name namenode --hostname namenode --rm -p 8088:8088 -v /hdfs/namenode:/hdfs/name shwsun/nn

docker run -it --privileged --name namenode --rm -p 8088:8088 -v /hdfs/namenode:/hdfs/name shwsun/nn /bin/bash
docker run -itd --privileged --name datanode --rm -p 8088:8088 -v /hdfs/datanode:/hdfs/data shwsun/dn

docker exec -it namenode jps


cd datanode
docker build -t shwsun/dn . 
docker run -it --privileged --name datanode --hostname datanode --rm -v /hdfs/datanode:/hdfs/data shwsun/dn
docker exec -it datanode jps
docker run -it --privileged --name datanode --rm -v /hdfs/datanode:/hdfs/data shwsun/dn /bin/bash
```

`$HADOOP_HOME/etc/hadoop/workers` 수정해서 서버 목록 지정  

```bash
cat <<EOF |tee $HADOOP_HOME/etc/hadoop/workers
dn01
dn02
dn03
EOF
```

## 클러스터 실행  
> 호스트에 /hdfs/namenode, /hdfs/dn01, /hdfs/dn02, /hdfs/dn03 을 볼륨 공유한다.   
namenode, datanode 생성이 끝나면 아래와 같이 실행  
```bash
# 아래와 같은 작업을 실행하는데, 간단하게 호출 스크립트 만들어 둠. 
# # cd hdfs-cluster
# rm -rdf /hdfs/
# docker-compose up
# ./sync_key_after_up.sh
# # node start 
# docker exec -u root -it namenode /hadoop/sbin/start-dfs.sh 
# # yarn start
# docker exec -u root -it namenode /hadoop/sbin/start-yarn.sh 
# #$HADOOP_HOME/bin/mapred --daemon start historyserver
cd /spark-git/spark/docker/hdfs-cluster 
./up.sh
# up 결과 확인 후 아래 실행.
./restart.sh
```

---  

Web UI  
NameNode (http://server01:9870)  
ResourceManager (http://server01:8088)  
MapReduce JobHistory Server (http://server01:19888)  

- host 에서 proxy 포트포워딩 위해 host의 /etc/hosts 에 docker network 정보 등록  
--> namenode, dn01, dn02, dn03 ip를 등록
```bash
docker network inspect hdfs-cluster_default
vi /etc/hosts
172.21.0.2 namenode
172.21.0.3 dn01
172.21.0.4 dn02
172.21.0.5 dn03
172.21.0.6 rdb
172.21.0.7 hue
```
  

--- 
# RDB 설치하기  
hue db, rdb, (hive metastore) 역할을 할 RDB를 설치  

---  
# Hue - HDFS Browser 연동하기  
Hue 실행을 root로 했다면, 아래와 같이 hue가 기본 접근하는 hdfs 경로 설정.  
이 설정은 `core-site.xml`의 `hadoop.proxyuser.<hue user>.hosts` 설정값과 같아야 한다.  
hue 계정이 'root' 이면, `hadoop.proxyuser.root.hosts` 로 property 추가해야 한다는 말.  

> [Errno 2] File /user/root not found
```bash
docker exec -it namenode hdfs dfs -mkdir -p /user/root
docker exec -it namenode hdfs dfs -chown -R root:supergroup /user
docker exec -it namenode hdfs dfs -chown -R root:supergroup /user/root
docker exec -it namenode hdfs dfs -chmod 755 /user
docker exec -it namenode hdfs dfs -chmod 755 /user/root
```
  
---  
# Hive 설치하기  
hadoop 설치가 완료되면, 이 중 hive job을 던지는 역할을 할 node 1대를 선정해서 해당 노드에 hive를 설치한다.  

## Hive metastore db 추가  
```sql
-- docker exec -it -u root rdb mysql
install plugin validate_password soname 'validate_password.so';
set global validate_password_policy=LOW;
set global validate_password_length=4;
CREATE USER 'hive'@'%' IDENTIFIED BY 'hive';

CREATE DATABASE metastore;
GRANT ALL privileges on metastore.* to 'hive'@'%' with GRANT option;
flush privileges;
exit;
```

```bash
docker exec -it dn01 /bin/bash  
####### install hive 
export HIVE_VER=3.1.2 
wget https://dlcdn.apache.org/hive/hive-${HIVE_VER}/apache-hive-${HIVE_VER}-bin.tar.gz
mkdir /hive
tar -xvf apache-hive-${HIVE_VER}-bin.tar.gz -C /hive

cat <<EOF |tee -a ~/.bashrc
export HIVE_HOME=/hive/apache-hive-${HIVE_VER}-bin
export PATH=\$PATH:\$HIVE_HOME/bin
EOF
source ~/.bashrc

# 1. hive-env.sh 설정 파일
echo "HADOOP_HOME=$HADOOP_HOME" > $HIVE_HOME/conf/hive-env.sh

##### 2 리모트 메타스토어 방식 설정 
# 하나에만 설치하면 되지만, 편의상 모든 데이터 노드에 설치했다.  
cat <<EOF |tee $HIVE_HOME/conf/hive-site.xml 
<?xml version="1.0" encoding="UTF-8" ?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
        <property>
            <name>hive.metastore.local</name>
            <value>false</value>
        </property>
        <property>
            <name>javax.jdo.option.ConnectionURL</name>
            <value>jdbc:mysql://rdb/metastore?characterEncoding=UTF-8&amp;useSSL=false&amp;user=hive&amp;password=hive</value>
        </property>
        <property>
            <name>javax.jdo.option.ConnectionDriverName</name>
            <value>com.mysql.jdbc.Driver</value>
        </property>

  <property>
    <name>javax.jdo.option.ConnectionUserName</name>
    <value>hive</value>
    <description>Username to use against metastore database</description>
  </property>
  <property>
    <name>javax.jdo.option.ConnectionPassword</name>
    <value>hive</value>
    <description>password to use against metastore database</description>
  </property>

  <property>
    <name>hive.server2.thrift.client.user</name>
    <value>hive</value>
    <description>Username to use against thrift client</description>
  </property>
  <property>
    <name>hive.server2.thrift.client.password</name>
    <value>hive</value>
    <description>Password to use against thrift client</description>
  </property>

        <property>
            <name>hive.exec.local.scratchdir</name>
            <value>/tmp/\${user.name}</value>
            <description>Local scratch space for Hive jobs</description>
        </property>
        <property>
            <name>hive.downloaded.resources.dir</name>
            <value>/tmp/\${user.name}_resources</value>
            <description>Temporary local directory for added resources in the remote file system.</description>
        </property>

<!-- hiveserver2 -->
        <property>
            <name>beeline.hs2.connection.user</name>
            <value>hive</value>
        </property>
        <property>
            <name>beeline.hs2.connection.password</name>
            <value>hive</value>
        </property>
        <property>
            <name>hive.server2.enable.doAs</name>
            <value>false</value>
        </property>
        <property>
            <name>hive.server2.authentication</name>
            <value>NONE</value>
        </property>

        <property>
            <name>hive.server2.enable.impersonation</name>
            <description>Enable user impersonation for HiveServer2</description>
            <value>false</value>
        </property> 
 <!-- update, delete 등을 지원하기 위하여 필요함 -->
        <property>
            <name>hive.support.concurrency</name>
            <value>true</value>
        </property>
        <property>
            <name>hive.enforce.bucketing</name>
            <value>true</value>
        </property>
        <property>
            <name>hive.exec.dynamic.partition.mode</name>
            <value>nonstrict</value>
        </property>
        <property>
            <name>hive.txn.manager</name>
            <value>org.apache.hadoop.hive.ql.lockmgr.DbTxnManager</value>
        </property>
        <property>
            <name>hive.compactor.initiator.on</name>
            <value>true</value>
        </property>
        <property>
            <name>hive.compactor.worker.threads</name>
            <value>4</value>
        </property>     

<property>
  <name>beeline.hs2.jdbc.url.tcpUrl</name>
  <value>jdbc:hive2://${hostname}:10000/metastore;user=hive;password=hive</value>
</property>
 
<property>
  <name>beeline.hs2.jdbc.url.httpUrl</name>
  <value>jdbc:hive2://${hostname}:11000/metastore;user=hive;password=hive;transportMode=http;httpPath=cliservice</value>
</property>
 
<property>
  <name>beeline.hs2.jdbc.url.default</name>
  <value>tcpUrl</value>
</property>   
</configuration>
EOF

# 5. guava version 맞추기    
rm $HIVE_HOME/lib/guava-19.0.jar
cp $HADOOP_HOME/share/hadoop/hdfs/lib/guava-27.0-jre.jar $HIVE_HOME/lib
# 6. jdbc driver classpath 등록  
pushd /install-files
wget https://downloads.mysql.com/archives/get/p/3/file/mysql-connector-java-5.1.49.tar.gz
tar -zxvf mysql-connector-java-5.1.49.tar.gz
cp mysql-connector-java-5.1.49/mysql-connector-java-5.1.49-bin.jar $HIVE_HOME/lib/
popd 

#### run hive 
# 6. init schema 
echo "---- Ready to init schama ----"
## 리모트 방식 
# 3. 하이브용 디렉토리 생성 및 확인 
hdfs dfs -mkdir -p /user/hive/warehouse
hdfs dfs -ls -R /user/hive
# 4. 쓰기 권한 추가 및 확인  
hdfs dfs -chmod g+w /user/hive/warehouse
hdfs dfs -ls -R /user/hive
#$HIVE_HOME/bin/schematool -dbType mysql -initSchema -userName hive -passWord hive
$HIVE_HOME/bin/schematool -dbType mysql -initSchema 
# 7. hive 서버 실행  
$HIVE_HOME/bin/hiveserver2
#$HIVE_HOME/bin/hive --service metastore 
echo "---- hiveserver2 started ----"
```
  
### hue hive 에서 연동 결과 테스트   
```sql
create database if not exists testdb;
use testdb;
create external table if not exists employee (
  eid int,
  ename string,
  age int,
  jobtype string,
  storeid int,
  storelocation string,
  salary bigint,
  yrsofexp int
)
row format delimited
fields terminated by ','
lines terminated by '\n'
stored as textfile location 'hdfs://namenode:9000/user/hive/warehouse/testdb.db/employee';
```
external 테이블을 생성한 후에 
Filebrowser 에서 /user/hive/warehouse/testdb.db/employee 경로에 employee.csv 파일을 업로드 한 후 셀렉트 해 본다.  


hive table은 mapreduce 설정이 된 상태에 작동한다.  
아래 명령 실행하고 insert 하면 에러 발생.  
mapreduce.framework.name
```sql
create table if not exists intbl (
  eid int,
  ename string);

insert into intbl values(1, 'a');
-- Error while processing statement: FAILED: Execution Error, return code 1 from org.apache.hadoop.hive.ql.exec.mr.MapRedTask. Cannot initialize Cluster. Please check your configuration for mapreduce.framework.name and the correspond server addresses.
```
--- 
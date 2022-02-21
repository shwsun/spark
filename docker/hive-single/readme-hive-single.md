# Hive Single node cluster  
hive single node 도커 이미지를 실행합니다.  
pseudo-distribution mode로 작동합니다.  

## 생성해 둔 이미지 실행하기  
```bash
docker run -itd --privileged --name hadoop --hostname hadoop --rm shwsun/hive-single
# detach 모드로 실행했기 때문에 hdfs 설치/실행 전에 도커 실행은 완료된다. 
# 아래 명령을 주기적으로 실행해서 name node 등이 목록에 표시되면 hdfs 준비된 것.
docker exec -it hadoop jps 
```
  
## CLI 실행  
```bash
docker exec -it hive-s /bin/bash
$HIVE_HOME/bin/beeline -n hive -p hive -u jdbc:mariadb://rdb:3306/metastore_db
beeline -n hive -p hive -u jdbc:hive2://hadoop:10000

# metastore 조사 
$HIVE_HOME/bin/schematool -dbType mysql -info -userName hive -passWord hive
```
  
## Hive 환경 생성하기  
```bash
# Dockerfile 이 위치한 경로에서  
# install-hadoop-single.sh 를 이용해 hdfs를 설치하고 
# install-hive-single.sh 를 이용해 hive를 연동하고 hiveserver2를 실행한다.  
docker build -t shwsun/hive-single .
docker login -u shwsun 
# password
docker push shwsun/hive-single
```







---  
# 구버전 설치 테스트  
```bash
# https://archive.apache.org/dist/hive/hive-2.1.1/apache-hive-2.1.1-bin.tar.gz

echo "---- Hive installation started. ----"
export HIVE_VER=2.1.1 # 2.3.9
wget https://archive.apache.org/dist/hive/hive-2.1.1/apache-hive-2.1.1-bin.tar.gz
mkdir /hive
tar -xvf apache-hive-${HIVE_VER}-bin.tar.gz -C /hive

cat <<EOF |tee -a ~/.bashrc
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=/hadoop/hadoop-3.2.2
export HIVE_HOME=/hive/apache-hive-${HIVE_VER}-bin
export PATH=\$PATH:\$JAVA_HOME/bin:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin:\$HIVE_HOME/bin
EOF
#source ~/.bashrc 
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=/hadoop/hadoop-3.2.2
export HIVE_HOME=/hive/apache-hive-${HIVE_VER}-bin
export PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$HIVE_HOME/bin

# mysql connector 
apt-get install libmysql-java
ln -s /usr/share/java/mysql-connector-java.jar $HIVE_HOME/lib/mysql-connector-java.jar
#
start-dfs.sh
start-yarn.sh

hdfs dfs -mkdir -p /user/hive/warehouse
hdfs dfs -mkdir -p /tmp/hive
hdfs dfs -chmod 777 /tmp/
hdfs dfs -chmod 777 /user/hive/warehouse
hdfs dfs -chmod 777 /tmp/hive

# mysql 
apt-get install -y mysql-server
service mysql start
mysql -u root -p  
CREATE DATABASE metastore_db;
USE metastore_db;
SOURCE /hive/apache-hive-3.1.2-bin/scripts/metastore/upgrade/mysql/hive-schema-0.14.0.mysql.sql;
CREATE USER 'hive'@'%' IDENTIFIED BY 'hive';
GRANT all on *.* to 'hive'@localhost identified by 'hive';
#grant all privileges on hive.* to 'hive'@'%' with grant option;
flush privileges;
exit


install plugin validate_password soname 'validate_password.so';
SHOW VARIABLES LIKE 'validate_password%';
set global validate_password_policy=LOW;
set global validate_password_length=4;
SELECT host, user, authentication_string password FROM mysql.user WHERE user='root';


<name>javax.jdo.option.ConnectionURL</name>
<value>jdbc:mysql://localhost/metastore_db?createDatabaseIfNotExist=true</value>



<property>
    <name>hive.exec.local.scratchdir</name>
    <value>/tmp/${user.name}</value>
    <description>Local scratch space for Hive jobs</description>
</property>

<property>
  <name>hive.downloaded.resources.dir</name>
  <value>/tmp/${user.name}_resources</value>
  <description>Temporary local directory for added resources in the remote file system.</description>
</property>


schematool -initSchema -dbType mysql
hive

# 1. hive-env.sh 설정 파일 
echo "HADOOP_HOME=$HADOOP_HOME" > $HIVE_HOME/conf/hive-env.sh
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
            <value>jdbc:mysql://localhost/metastore_db?createDatabaseIfNotExist=true</value>
        </property>
        <property>
            <name>javax.jdo.option.ConnectionDriverName</name>
            <value>org.mysql.jdbc.Driver</value>
        </property>
        <property>
            <name>javax.jdo.option.ConnectionUserName</name>
            <value>hive</value>
        </property>
        <property>
            <name>javax.jdo.option.ConnctionPassword</name>
            <value>hive</value>
        </property>
        <property>
            <name>hive.exec.local.scratchdir</name>
            <value>/tmp/${user.name}</value>
            <description>Local scratch space for Hive jobs</description>
        </property>
        <property>
            <name>hive.downloaded.resources.dir</name>
            <value>/tmp/${user.name}_resources</value>
            <description>Temporary local directory for added resources in the remote file system.</description>
        </property>
</configuration>
EOF
```
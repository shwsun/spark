# install-hadoop-single.sh 
echo "---- Hive installation started. ----"
export HIVE_VER=3.1.2 # 2.3.9
wget https://dlcdn.apache.org/hive/hive-${HIVE_VER}/apache-hive-${HIVE_VER}-bin.tar.gz
mkdir /hive
tar -xvf apache-hive-${HIVE_VER}-bin.tar.gz -C /hive

cat <<EOF |tee -a ~/.bashrc
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=/hadoop/hadoop-3.3.1
export HIVE_HOME=/hive/apache-hive-${HIVE_VER}-bin
export PATH=\$PATH:\$JAVA_HOME/bin:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin:\$HIVE_HOME/bin
EOF
#source ~/.bashrc 
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=/hadoop/hadoop-3.3.1
export HIVE_HOME=/hive/apache-hive-${HIVE_VER}-bin
export PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$HIVE_HOME/bin

# 1. hive-env.sh 설정 파일 
echo "HADOOP_HOME=$HADOOP_HOME" > $HIVE_HOME/conf/hive-env.sh
##### 2 리모트 메타스토어 방식 설정 
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
            <value>jdbc:mysql://localhost/metastore_db?createDatabaseIfNotExist=true</value>
        </property>
        <property>
            <name>javax.jdo.option.ConnectionDriverName</name>
            <value>com.mysql.jdbc.Driver</value>
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
            <value>true</value>
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
  <value>jdbc:hive2://localhost:10000/metastore_db;user=hive;password=hive</value>
</property>
 
<property>
  <name>beeline.hs2.jdbc.url.httpUrl</name>
  <value>jdbc:hive2://localhost:10000/metastore_db;user=hive;password=hive;transportMode=http;httpPath=cliservice</value>
</property>
 
<property>
  <name>beeline.hs2.jdbc.url.default</name>
  <value>tcpUrl</value>
</property>   
</configuration>
EOF

# docker 생성 시점에는 아직 hadoop run하지 않은 상태
# 3. 하이브용 디렉토리 생성 및 확인 
hdfs dfs -mkdir -p /user/hive/warehouse
hdfs dfs -ls -R /user/hive
# 4. 쓰기 권한 추가 및 확인  
hdfs dfs -chmod g+w /user/hive/warehouse
hdfs dfs -ls -R /user/hive
# 5. guava version 맞추기    
rm $HIVE_HOME/lib/guava-19.0.jar
cp $HADOOP_HOME/share/hadoop/hdfs/lib/guava-27.0-jre.jar $HIVE_HOME/lib
# 6. jdbc driver classpath 등록  
pushd /install-files
#wget https://downloads.mariadb.com/Connectors/java/connector-java-2.7.3/mariadb-java-client-2.7.3.jar
# wget https://dlm.mariadb.com/1936500/Connectors/java/connector-java-3.0.3/mariadb-java-client-3.0.3.jar
# chmod 644 mariadb-java-client-3.0.3.jar
# cp mariadb-java-client-3.0.3.jar $HIVE_HOME/lib/mariadb-java-client.jar
# apt-get install libmysql-java
# ln -s /usr/share/java/mysql-connector-java.jar $HIVE_HOME/lib/mysql-connector-java.jar

wget https://downloads.mysql.com/archives/get/p/3/file/mysql-connector-java_8.0.27-1ubuntu18.04_all.deb
dpkg -i mysql-connector-java_8.0.27-1ubuntu18.04_all.deb
#tar -zxvf mysql-connector-java-8.0.27.tar.gz 
cp /usr/share/java/mysql-connector-java-8.0.27.jar $HIVE_HOME/lib/
popd 

# ---- mysql install & run 
# mysql 
apt-get install -y mysql-server
service mysql start
#service mysql restart
cat <<EOF |tee /install-files/metastore-creation.sh
install plugin validate_password soname 'validate_password.so';
set global validate_password_policy=LOW;
set global validate_password_length=4;
CREATE USER 'hive'@'%' IDENTIFIED BY 'hive';
CREATE DATABASE metastore_db;
GRANT ALL privileges on *.* to 'hive'@'%' with GRANT option;
flush privileges;
EOF

mysql -u root -p"\n" < /install-files/metastore-creation.sh

# 6. init schema 
echo "---- Ready to init schama ----"
## 리모트 방식 
$HIVE_HOME/bin/schematool -dbType mysql -initSchema -userName hive -passWord hive
#$HIVE_HOME/bin/schematool -dbType mysql -initSchema 
# 7. hive 서버 실행  
$HIVE_HOME/bin/hiveserver2
#$HIVE_HOME/bin/hive --service metastore 
echo "---- hiveserver2 started ----"




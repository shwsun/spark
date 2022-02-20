# install-hadoop-single.sh 
echo "---- Hive installation started. ----"
export HIVE_VER=3.1.2 # 2.3.9
wget https://dlcdn.apache.org/hive/hive-${HIVE_VER}/apache-hive-${HIVE_VER}-bin.tar.gz
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
                <value>jdbc:mariadb://rdb:3306/metastore_db</value>
        </property>
        <property>
                <name>javax.jdo.option.ConnectionDriverName</name>
                <value>org.mariadb.jdbc.Driver</value>
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
            <name>hive.metastore.uris</name>
            <value>thrift://localhost:9083</value>
            <description>IP address (or fully-qualified domain name) and port of the metastore host</description>
        </property>
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

# for postgre md5 password generation 
#echo -n "1234" | md5sum | awk '{print $1}' 
# md581dc9bdb52d04dc20036dbd8313ed055

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
wget https://downloads.mariadb.com/Connectors/java/connector-java-2.7.3/mariadb-java-client-2.7.3.jar
chmod 644 mariadb-java-client-2.7.3.jar
cp mariadb-java-client-2.7.3.jar $HIVE_HOME/lib/mariadb-java-client.jar
popd 
# 6. init schema 
echo "---- Ready to init schama ----"
## 리모트 방식 
#$HIVE_HOME/bin/schematool -dbType mysql -initSchema -userName hive -passWord hive
#$HIVE_HOME/bin/schematool -dbType mysql -initSchema 
# 7. hive 서버 실행  
#$HIVE_HOME/bin/hiveserver2
#$HIVE_HOME/bin/hive --service metastore 
echo "---- hiveserver2 started ----"




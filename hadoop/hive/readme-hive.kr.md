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
# 1. hive-env.sh 설정 파일 
echo "HADOOP_HOME=$HADOOP_HOME" > $HIVE_HOME/conf/hive-env.sh
# 2. hive-site.xml 파일 생성. hive-default.xml.template -> hive-site.xml 
cp $HIVE_HOME/conf/hive-default.xml.template $HIVE_HOME/conf/hive-site.xml
# # 
# cat <<EOF |tee $HIVE_HOME/conf/hive-site.xml
# <?xml version="1.0" encoding="UTF-8" standalone="no"?>
# <?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
# <configuration>
#   <property>
#        <name>hive.metastore.warehouse.dir</name>
#        <value>/user/hive/warehouse</value>
#   </property>
#   <property>
#        <name>hive.cli.print.header</name>
#        <value>true</value>
#   </property>
#   <property>
#     <name>javax.jdo.option.ConnectionURL</name>
#     <value>jdbc:derby:;databaseName=metastore_db;create=true</value>
#   </property>

#   <property>
#     <name>javax.jdo.option.ConnectionDriverName</name>
#     <value>org.apache.derby.jdbc.EmbeddedDriver</value>
#   </property>

#   <property>
#     <name>javax.jdo.option.ConnectionUserName</name>
#     <value>user</value>
#   </property>

#   <property>
#     <name>javax.jdo.option.ConnectionPassword</name>
#     <value>password</value>
#   </property>
# </configuration>
# EOF

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
cd $HIVE_HOME
$HIVE_HOME/bin/schematool -dbType derby -initSchema
# relative path 에러 발생 시 초기화 경로 관련 설정을 추가 
# In the hive-site.xml, replace ${system:java.io.tmpdir}/${system:user.name} by /tmp/mydir as what has been told in
# metastore 정보 확인 
# hive --service schemaTool -dbType derby -info -userName user --passWord password

# 6. hive 서버 실행  
# Running HiveServer2 and Beeline
#cd /hive-meta;$HIVE_HOME/bin/hiveserver2
$HIVE_HOME/bin/hiveserver2
# $HIVE_HOME/bin/beeline -u jdbc:hive2://$HS2_HOST:$HS2_PORT
# $HIVE_HOME/bin/beeline -u jdbc:hive2://172.17.0.3:10000/default
# $HIVE_HOME/bin/beeline -u jdbc:hive2://localhost:10000
# !connect jdbc:hive2://<host>:<port>/<db>;auth=noSasl
#cd /hive-meta;$HIVE_HOME/bin/beeline -u jdbc:derby:metastore_db;databaseName=metastore_db;create=true
$HIVE_HOME/bin/beeline -u jdbc:derby:metastore_db;databaseName=metastore_db;create=true

#!connect jdbc:derby:metastore_db;databaseName=metastore_db;create=true

# sample HiveQL 
# create table test_first(id int);
# insert into test_first(id) values(222);
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
  
thrift(10000) 설정과 hadoop user 설정 등 확인해 보고 다시 실행해 본다.  
```bash
#hadoop core-site 추가 property
<property>
<name>hadoop.proxyuser.dikshant.groups</name>
<value>*</value>
</property>
<property>
<name>hadoop.proxyuser.dikshant.hosts</name>
<value>*</value>
</property>
<property>
<name>hadoop.proxyuser.server.hosts</name>
<value>*</value>
</property>
<property>
<name>hadoop.proxyuser.server.groups</name>
<value>*</value>
</property>
```
위의 dikshant 이용해서 아래와 같이 연결해 본다.  
```bash
beeline -n dikshant -u jdbc:hive2://localhost:10000
```
  
- beeline -u jdbc:hive2://  
hive-site.xml 에 아래와 같은 내용 추가  
```bash
# 치환
#sed 's/addrass/address/' list.txt
# 삭제 
#sed '/addrass/d' list.txt
# 실행 
cat $HIVE_HOME/conf/hive-site.xml | sed 's/</configuration>/#insert_new_prop/g'| > $HIVE_HOME/conf/hive-site.xml
cat << EOF |tee -a $HIVE_HOME/conf/hive-site.xml 
  <property>
    <name>system:java.io.tmpdir</name>
    <value>/tmp/hive/java</value>
  </property>
  <property>
    <name>system:user.name</name>
    <value>${user.name}</value>
  </property>
</configuration>
EOF
```
```xml
  <property>
    <name>system:java.io.tmpdir</name>
    <value>/tmp/hive/java</value>
  </property>
  <property>
    <name>system:user.name</name>
    <value>${user.name}</value>
  </property>
```
---  


> run hue container 
```bash
docker run -it -p 8888:8888 gethue/hue:latest
docker run -it -u root --name hue -p 8088:8888 gethue/hue:latest
#http://34.125.237.158:8088/
```
  
# build Hue docker 
```bash
# hue apt install 진행하기 위해 root로 로그인  
# docker run hue -> login root -> intall & config -> commit -> push custom hue image 
# docker exec -it hue -u root /bin/bash 

docker build https://github.com/cloudera/hue.git#release-4.10.0 -t gethue/hue:4.10.0 -f tools/docker/hue/Dockerfile
docker tag gethue/hue:4.10.0 gethue/hue:latest
docker images
docker login -u gethue
docker push gethue/hue
docker push gethue/hue:4.10.0

docker build https://github.com/cloudera/hue.git#release-4.10.0 -t gethue/nginx:4.10.0 -f tools/docker/nginx/Dockerfile;
docker tag gethue/nginx:4.10.0 gethue/nginx:latest
docker push gethue/nginx
docker push gethue/nginx:4.10.0
```
# Hive 
hdfs-single 에 Hive를 추가한다.  

> run hue container 
```bash
docker run -it -p 8888:8888 gethue/hue:latest
docker run -it -u root --name hue -p 8088:8888 gethue/hue:latest
#http://34.125.237.158:8088/
```
  
---  
# Hive install & Run  
1. hive 설치 파일 다운로드 및 압축 해제 
```bash
# docker exec -it hdfs-single /bin/bash 
wget https://dlcdn.apache.org/hive/hive-2.3.9/apache-hive-2.3.9-bin.tar.gz
mkdir /hive
tar -xvf apache-hive-2.3.9-bin.tar.gz -C /hive
```
2. 환경변수 설정 
 - .bashrc 
```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=/hadoop/hadoop-3.2.2
export HIVE_HOME=/hive/apache-hive-2.3.9-bin
#export PATH=$PATH:/hive/apache-hive-2.3.9-bin/bin
export PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$HIVE_HOME/bin
```
 - source .bashrc 

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
echo "HADOOP_HOME=/hadoop/hadoop-3.2.2" > $HIVE_HOME/conf/hive-env.sh
# 2. hive-site.xml 파일 생성  
cat <<EOF |tee $HIVE_HOME/conf/hive-site.xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
  <property>
       <name>hive.metastore.warehouse.dir</name>
       <value>/user/hive/warehouse</value>
  </property>
  <property>
       <name>hive.cli.print.header</name>
       <value>true</value>
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
schematool -dbType derby -initSchema


```

하이브 실행 : hive  
  
---  
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
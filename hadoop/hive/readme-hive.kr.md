# Hive 
hdfs-single 에 Hive를 추가한다.  

> run hue container 
```bash
docker run -it -p 8888:8888 gethue/hue:latest
#http://34.125.237.158:8088/
```

1. hive 설치 파일 다운로드 및 압축 해제 
2. 환경변수 설정 
 - .bashrc 
```bash
export JAVA_HOME=/usr/java/jdk1.7.0_80
export HADOOP_HOME=/home/hadoop/hadoop-2.7.2
export HIVE_HOME=/home/hadoop/apache-hive-2.0.0-bin
export PATH
```
 - source .bashrc 

cp hive-env.sh.template hive-env.sh  
hive-env.sh 수정  
HADOOP_HOME=/home/hadoop/hadoop-2.7.2  
hive-site.xml 파일 생성  
```xml
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
```
하이브용 디렉토리 생성 및 확인  
hdfs dfs -mkdir -p /user/hive/warehouse
hdfs dfs -ls -R /user/hive
쓰기 권한 추가 및 확인  
hdfs dfs -chmod g+w /user/hive/warehouse
hdfs dfs -ls -R /user/hive
schematool 띄우기  
schematool -dbType derby -initSchema
하이브 실행 : hive  

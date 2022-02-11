# Hadoop Install & Run  
Apache Hadoop을 설치하고 실행하는 방법을 설명합니다.  
Single Cluster mode로 먼저 설치하고 Cluster mode로 변경합니다.  
  
Cluster 설치를 container에서 진행하고 이를 재사용 합니다.  


# Hadoop Single Cluster  
container 설치 과정은 [Hdfs on Docker]()를 참고합니다.  
  
미리 작성해 둔 container image를 이용해 Hadoop을 Single Cluster로 실행하고 사용해 봅니다.  
  
## Hadoop 실행하기  

```bash
sudo -i
docker run -itd --privileged --name hdfs --hostname hdfs --rm shwsun/hdfs:single 
docker exec -it hdfs /bin/bash 

# in hdfs container 
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
export HADOOP_HOME=/hadoop/hadoop-3.2.2
cd $HADOOP_HOME
mkdir input
cp etc/hadoop/*.xml input
bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.2.jar grep input output 'dfs[a-z.]+'
cat output/*
# rm -rdf input output
```

pseudo-dist 로 설정한 경우에는 local 방식으로 접근시 에러 발생한다.  
  
bin/hdfs dfs -ls hdfs://127.0.0.1:9000 은 정상적으로 처리  
 -> hdfs://172.17.0.3:9000 은 연결 거절된다.  
bin/hdfs dfs -ls hdfs://172.17.0.3:9000 
   
xml 설정 변경해서 외부 연결 가능하게 변경하고 다시 테스트  
```bash
export HADOOP_HOME=/hadoop/hadoop-3.2.2
cd $HADOOP_HOME
sbin/stop-dfs.sh
cat <<EOF|tee $HADOOP_HOME/etc/hadoop/core-site.xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://172.17.0.3:9000</value>
    </property>
</configuration>
EOF

sbin/start-dfs.sh
```

#### 원격 client spark 에서 hdfs 접근 확인  
```scala
val textDF = spark.read.textFile("hdfs://172.17.0.3:9000/user/root/output")
textDF.show()
```

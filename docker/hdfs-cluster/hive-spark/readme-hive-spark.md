# Hive-Spark node container   
## Specification 
- Hadoop : 3.2.2 
- Hive : 3.1.2 (log4j 2.17.2 - vulnerability fix)   
- Yarn : 
- Hue : 4
- Spark : 3.1.3  
  

## build 
```bash
docker build -t shwsun/hive-spark . 
docker push shwsun/hive-spark  
```

## Spark-Yarn  
Spark yarn cluster 에서는 client 나 driver 에만 spark가 존재하면 된다.  
Spark cluster를 별도로 start 하지 않아도 Yarn 설정에 따라 Spark slave 들이 작동한다.  
 -> 현재는 각각의 data 노드에도 spark 를 모두 설치한 상태.  
>> -> Spark을 제거한 상태에서도 테스트 해 본다.  
  
---  
## log4j 취약점 확인  
- dn01  
```bash
root@dn01:/install-files# find / -name 'log4j*'
/usr/local/lib/python3.6/dist-packages/pyspark/jars/log4j-1.2.17.jar
/spark/conf/log4j.properties.template
/hadoop/share/hadoop/common/lib/log4j-1.2.17.jar
/hadoop/share/hadoop/tools/sls/sample-conf/log4j.properties
/hadoop/share/hadoop/hdfs/lib/log4j-1.2.17.jar
/hadoop/etc/hadoop/log4j.properties
/hive-bin/apache-hive-3.1.2-bin/lib/log4j-slf4j-impl-2.10.0.jar
/hive-bin/apache-hive-3.1.2-bin/lib/log4j-core-2.10.0.jar
/hive-bin/apache-hive-3.1.2-bin/lib/log4j-api-2.10.0.jar
/hive-bin/apache-hive-3.1.2-bin/lib/log4j-web-2.10.0.jar
/hive-bin/apache-hive-3.1.2-bin/lib/log4j-1.2-api-2.10.0.jar
```
  
---  
## Livy 설치  
spark-master 에 livy server를 설치하고 실행하면, hue 에서 job-livy를 조회할 수 있다.  
hue notebook pyspark에 livy를 연결하면, 편집기를 이용해 livy를 호출할 수 있다.  
단, spark 3.x 에서는 livy 호출 시 아래와 같은 에러가 발생한다.  
이 에러를 처리해야 사용할 수 있다.  
```bash
The Spark session is dead and could not be created in the cluster: at org.apache.spark.deploy.SparkSubmit.doSubmit(SparkSubmit.scala:90) at org.apache.spark.deploy.SparkSubmit$$anon$2.doSubmit(SparkSubmit.scala:1039) at org.apache.spark.deploy.SparkSubmit$.main(SparkSubmit.scala:1048) at org.apache.spark.deploy.SparkSubmit.main(SparkSubmit.scala) Caused by: java.lang.ClassNotFoundException: scala.Function0$class at java.net.URLClassLoader.findClass(URLClassLoader.java:387) at java.lang.ClassLoader.loadClass(ClassLoader.java:418) at java.lang.ClassLoader.loadClass(ClassLoader.java:351) ... 20 more 2022-03-10 06:22:21,062 INFO util.ShutdownHookManager: Shutdown hook called
```
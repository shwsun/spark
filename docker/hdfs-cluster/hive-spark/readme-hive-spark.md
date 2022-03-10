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
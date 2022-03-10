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
docker run -itd --privileged --name hdfs-single --hostname hdfs-single --rm shwsun/hdfs-single:1.0 
# hdfs 실행에 3~4분 시간 걸린다. 
# 아래 명령으로 확인해서 data node 가 표시되면,  hdfs://172.17.0.3:9000 으로 준비 완료. 
docker exec -it hdfs-single jps
```

> pseudo-dist 로 설정한 경우에는 local 방식으로 접근시 에러 발생한다.  

#### 원격 client spark 에서 hdfs 접근 확인  
```scala
val textDF = spark.read.textFile("hdfs://172.17.0.3:9000/user/root/output")
textDF.show()
```
```python
spark.read.text("hdfs://172.17.0.3:9000/user/root/input").show()
# /user/root/input 이 존재하지 않기 때문에 에러 발생하는 것이 정상.
# 확인 후, 데이터를 쓰고 읽어본다.  
```

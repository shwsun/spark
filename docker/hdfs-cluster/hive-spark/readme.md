# Hive-Spark node container   
## Specification 
- Hadoop : 3.2.2 
- Hive : 3.1.2  
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
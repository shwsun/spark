# HDFS cluster  
1. namenode hdfs 실행  
2. datanode hdfs 실행  

```bash
docker build -t nn-tmp . 
docker run -itd --privileged --name namenode --hostname namenode --rm -p 8088:8088 -v /hdfs/namenode:/hdfs/name nn-tmp

docker run -it --privileged --name namenode --rm -p 8088:8088 -v /hdfs/namenode:/hdfs/name nn-tmp /bin/bash
docker run -itd --privileged --name datanode --rm -p 8088:8088 -v /hdfs/datanode:/hdfs/data dn-tmp

docker exec -it namenode jps
```

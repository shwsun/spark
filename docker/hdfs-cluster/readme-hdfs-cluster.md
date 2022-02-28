# HDFS cluster  
1. namenode hdfs 실행  
2. datanode hdfs 실행  

```bash
docker build -t shwsun/nn . 
docker run -it --privileged --name namenode --hostname namenode --rm -p 8088:8088 -v /hdfs/namenode:/hdfs/name shwsun/nn

docker run -it --privileged --name namenode --rm -p 8088:8088 -v /hdfs/namenode:/hdfs/name shwsun/nn /bin/bash
docker run -itd --privileged --name datanode --rm -p 8088:8088 -v /hdfs/datanode:/hdfs/data shwsun/dn

docker exec -it namenode jps



docker build -t shwsun/dn . 
docker run -it --privileged --name datanode --hostname datanode --rm -v /hdfs/datanode:/hdfs/data shwsun/dn
docker exec -it datanode jps
docker run -it --privileged --name datanode --rm -v /hdfs/datanode:/hdfs/data shwsun/dn /bin/bash
```

`$HADOOP_HOME/etc/hadoop/workers` 수정해서 서버 목록 지정  

```bash
cat <<EOF |tee $HADOOP_HOME/etc/hadoop/workers
namenode
datanode
EOF
```

## 클러스터 실행  
namenode, datanode 생성이 끝나면 아래와 같이 실행  
```bash
# namenode의 ssh key를 datanode로 복사  
docker cp namenode:/root/.ssh/authorized_keys /spark-git/spark/docker/hdfs-cluster/authorized_keys
docker cp /spark-git/spark/docker/hdfs-cluster/authorized_keys datanode:/root/.ssh/authorized_keys
docker exec -u root -it datanode /etc/init.d/ssh start
# node start 
docker exec -u root -it namenode /hadoop/sbin/start-dfs.sh 
docker exec -u root -it namenode /hadoop/sbin/start-yarn.sh 
```
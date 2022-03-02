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
> 호스트에 /hdfs/namenode, /hdfs/dn01, /hdfs/dn02, /hdfs/dn03 을 볼륨 공유한다.   
namenode, datanode 생성이 끝나면 아래와 같이 실행  
```bash
# # namenode의 ssh key를 datanode로 복사  
# docker cp namenode:/root/.ssh/authorized_keys /spark-git/spark/docker/hdfs-cluster/authorized_keys
# docker cp /spark-git/spark/docker/hdfs-cluster/authorized_keys datanode:/root/.ssh/authorized_keys
# docker exec -u root -it datanode /etc/init.d/ssh start
# cd docker/hdfs-cluster
# chmod 755 ./sync_key_after_up.sh

# cd hdfs-cluster
# rm -rdf /hdfs/
docker-compose up
# hdfs/data 와 namenode:/knownhosts 삭제하고 실행해야 한다. 
# knownetworks 삭제 
./sync_key_after_up.sh
# node start 
docker exec -u root -it namenode /hadoop/sbin/start-dfs.sh 
# yarn start
docker exec -u root -it namenode /hadoop/sbin/start-yarn.sh 
#$HADOOP_HOME/bin/mapred --daemon start historyserver

docker exec -u root -it namenode jps
docker exec -u root -it dn01 jps
```

모든 DataNode에서 수행할 것  
```bash
rm -rf $HADOOP_HOME/data/datanode/*  
```
  
Web UI  
NameNode (http://server01:9870)  
ResourceManager (http://server01:8088)  
MapReduce JobHistory Server (http://server01:19888)  

- host 에서 proxy 포트포워딩 위해 host의 /etc/hosts 에 docker network 정보 등록  
--> namenode, dn01, dn02, dn03 ip를 등록
```bash
docker network inspect hdfs-cluster_default
vi /etc/hosts
172.21.0.2 namenode
172.21.0.3 dn01
172.21.0.4 dn02
172.21.0.5 dn03
172.21.0.6 rdb
172.21.0.7 hue
```
  

--- 
# RDB 설치하기  
hue db, rdb, (hive metastore) 역할을 할 RDB를 설치  

---  
# Hue 연동하기  

  
---  
# Hive 설치하기  
hadoop 설치가 완료되면, 이 중 hive job을 던지는 역할을 할 node 1대를 선정해서 해당 노드에 hive를 설치한다.  

--- 
# HDFS Single node cluster  
hdfs single node 도커 이미지를 실행합니다. 

```bash
docker run -itd --privileged --name hdfs-single --hostname hdfs-single --rm -p 10000:10000 shwsun/hdfs-single:1.0
# detach 모드로 실행했기 때문에 hdfs 설치/실행 전에 도커 실행은 완료된다. 
# 아래 명령을 주기적으로 실행해서 name node 등이 목록에 표시되면 hdfs 준비된 것.
docker exec -it hdfs-single jps 
```

---  

hdfs single 도커 이미지를 재사용하지 않고 직접 생성하려면 아래와 같이 진행합니다.  
```bash
cd hdfs-single 
docker run -itd --privileged --name spark-hdfs --hostname spark-hdfs --rm ubuntu:18.04
docker cp install-hadoop-single.sh spark-hdfs:/shells/install-hadoop-single.sh 
docker exec -it spark-hdfs /bin/bash  

# in docker shell 
chmod 755 /shells/install-hadoop-single.sh  
/shells/install-hadoop-single.sh  
export HADOOP_HOME=/hadoop/hadoop-3.2.2
cd $HADOOP_HOME
# 1. Format the filesystem: 
bin/hdfs namenode -format
# 2. Start NameNode daemon and DataNode daemon:
sbin/start-dfs.sh
```

이미지 빌드  
```bash
cd hdfs-single 
docker build -t shwsun/hdfs-single .
```
# Hive Single node cluster  
hive single node 도커 이미지를 실행합니다.  
pseudo-distribution mode로 작동합니다.  

## 생성해 둔 이미지 실행하기  
```bash
docker run -itd --privileged --name hive-s --hostname hive-s -p 10000:10000 --rm shwsun/hive-single
# detach 모드로 실행했기 때문에 hdfs 설치/실행 전에 도커 실행은 완료된다. 
# 아래 명령을 주기적으로 실행해서 name node 등이 목록에 표시되면 hdfs 준비된 것.
docker exec -it hive-s jps 
```
  
## CLI 실행  
```bash
docker exec -it hive-s /bin/bash
$HIVE_HOME/bin/beeline -n postgres -p 1234 -u jdbc:postgresql://rdb:5432/metastore_db
```
  
## Hive 환경 생성하기  
```bash
# Dockerfile 이 위치한 경로에서  
# install-hadoop-single.sh 를 이용해 hdfs를 설치하고 
# install-hive-single.sh 를 이용해 hive를 연동하고 hiveserver2를 실행한다.  
docker build -t shwsun/hive-single .
docker login -u shwsun 
# password
docker push shwsun/hive-single
```


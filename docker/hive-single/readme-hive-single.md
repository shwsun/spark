# Hive Single node cluster  
hive single node 도커 이미지를 실행합니다. 

```bash
docker run -itd --privileged --name hive-s --hostname hive-s --rm shwsun/hive-single:1.0
# detach 모드로 실행했기 때문에 hdfs 설치/실행 전에 도커 실행은 완료된다. 
# 아래 명령을 주기적으로 실행해서 name node 등이 목록에 표시되면 hdfs 준비된 것.
docker exec -it hive-s jps 
```

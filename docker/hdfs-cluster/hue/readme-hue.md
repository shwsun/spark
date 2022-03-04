# Hue 연동하기  
*** 주의사항 ***  
>root 로 hue 계정 생성해야 추가 설정없이 Filebrowser 사용 가능  
>hue.ini 에소 hdfs superuser를 root로 지정했기 때문.  
>Yarn RM을 실행해 두어야 `Job` 연동 가능  
>`Workflow` 연동위해서는 `Oozie` 설치하고 `hue.ini`에 설정 추가해야  
>`hive-metastore-postgresql`에 psql 로 `hue` db/user 생성행 두어야 함.  
  

Hue container , Hive 서버 연동하기 위한 설정 생성하기    
```bash
# 설정 편집하기  
docker run -it -u root --name hue-tmp --net hdfs-cluster_default -p 8889:8888 gethue/hue:latest /bin/bash
docker run -it -u root --name hue-tmp -p 8889:8888 shwsun/hue /bin/bash
# 편집 저장하기  
docker cp hue-conf/hue.ini hue-tmp:/usr/share/hue/desktop/conf/hue.ini

# 설정 변경 저장 
docker commit hue-tmp shwsun/hue
docker login -u shwsun 
docker push shwsun/hue

docker run -it --privileged -u root --name hue --net hdfscluster_default -p 8890:8888 shwsun/hue ./startup.sh
docker run -it --privileged -u root --name hue --net hive-comp_default -p 8888:8888 gethue/hue:latest ./startup.sh

docker run -it --privileged -u root --name hue-tmp -p 8888:8888 shwsun/hue /bin/bash
docker cp hue-conf/hue.ini hue-tmp:/usr/share/hue/desktop/conf/hue.ini

```
현재 hadoop cluster가 yarn 을 실행하지 않은 상태라, Hue에서 Job 을 연동하려면 namenode 에서 아래와 같이 yarn Resource Manager를 실행해야 함.  
```bash
#in namenode 
yarn resourcemanager start & 
```

## hue db 생성 
```bash
sudo -u postgres psql
postgres=# create database hue with lc_collate='en_US.utf8';
CREATE DATABASE
postgres=# create user hue with password '1234';
CREATE ROLE
postgres=# grant all privileges on database hue to hue;
GRANT
```
```bash
# psql -h 호스트 -U 사용자 -d 데이터베이스 
psql -h rdb -U hue -d hue
psql -U hue -d hue
#Password for user hue => 입력
hue=> \q
```
  
## 연동 Hue 실행하기  
```bash
```

## Hue <-> Filebrowser 에러  
403 error : `User: root is not allowed to impersonate root`    
hdfs dfs -mkdir -p /user/root
hdfs dfs -chown -R root:supergroup /user
hdfs dfs -chown -R root:supergroup /user/root
hdfs dfs -chmod 755 /user
hdfs dfs -chmod 755 /user/root
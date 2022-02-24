# Hue 연동하기  

Hue container , Hive 서버 연동하기 위한 설정 생성하기    
```bash
# 설정 편집하기  
docker run -it -u root --name hue-tmp --net hive-comp_default -p 8889:8888 gethue/hue:latest /bin/bash

# 편집 저장하기  
docker cp ./hive-comp/hue-conf/hue.ini hue-tmp:/usr/share/hue/desktop/conf/hue.ini

# 설정 변경 저장 
docker commit hue-tmp shwsun/hue
docker login -u shwsun 
docker push shwsun/hue

docker run -it --privileged -u root --name hue --net hive-comp_default -p 8888:8888 shwsun/hue ./startup.sh
docker run -it --privileged -u root --name hue --net hive-comp_default -p 8888:8888 gethue/hue:latest ./startup.sh
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
psql -h rdb -U hue_u -d hue_d
psql -U hue_u -d hue_d
Password for user hue_u:
hue=> \q
```
  
## 연동 Hue 실행하기  
```bash
```
# MySql  
- 이미지 빌드  
```bash
docker build -t mysql-tmp .
```

- 사용하기  
```bash
docker run -it --name mysql -d mysql-tmp 
docker exec -it mysql /bin/bash
```

```sql
-- 172.17.0.2 
show databases;
select host, user, authentication_string from mysql.user;
quit;
```

```bash
# image buile
docker build -t mysql-tmp .
# modify container
docker run -it --name mysql -d mysql-tmp 
docker exec -it mysql /bin/bash
# tagging 
docker commit mysql-tmp 
docker tag mysql-tmp shwsun/mysql-hue
# push 
docker push shwsun/mysql-hue
# init & run 
docker stop mysql
docker rm mysql 
docker run -it --name mysql -d shwsun/mysql-hue 
docker exec -it mysql /bin/bash  


# hive
#mysql -h172.17.0.2 -uhive -phive -Dmetastore  

#==> ERROR 2003 (HY000)
# grep ^bind-address /etc/mysql/my.cnf 
# vi /etc/mysql/mysql.conf.d/mysqld.cnf
# bind-address 0.0.0.0
```

## Hue database 생성  
```bash
docker run -it --name mysql-tmp -d mysql 
docker exec -it mysql-tmp /bin/bash

docker run -it --name mysql-tmp --net hdfs-cluster_default -d mysql
```
```sql
set global validate_password_policy=LOW;
set global validate_password_length=3;
CREATE USER 'hue_u'@'%' IDENTIFIED BY 'hue_pwd';
CREATE DATABASE hue_db;
GRANT ALL privileges on hue_db.* to 'hue_u'@'%' with GRANT option;
flush privileges;
```
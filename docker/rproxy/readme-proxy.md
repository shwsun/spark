# Reverse Proxy  
Cluster Web UI 호출에 사용할 proxy 설정  


```bash
# nginx -s reload
docker run -it --name rproxy --net hdfs-cluster_default -p 80:80 -d nginx
```

```Dockerfile
#/etc/nginx/conf.d/default.conf 에서 수정해야 
FROM nginx
COPY default.conf /etc/nginx/conf.d/default.conf
```


```bash
#docker/proxy 
docker build -t shwsun/rproxy .
docker push shwsun/rproxy

docker run -it --name rproxy --net hdfs-cluster_default -p 80:80 -d shwsun/rproxy /bin/bash

```

## proxy 설정 수정하기 
로컬 파일에서 수정한 설정값을 컨테이너에 직접 반영하는 방법  
```bash
# rproxy 경로에서 실행 
docker cp default.conf rproxy:/etc/nginx/conf.d/default.conf
docker exec -u root --privileged -it rproxy  nginx -s reload
```


## 서비스 등록하기  
```bash
#code-server --bind-addr 0.0.0.0:80 > /dev/null 2>&1 &  
vi /etc/systemd/system/rproxy.service

# <service name>.service
[Unit]
Description=Reverse proxy Service
Requires=docker.service
[Service]
User=root
WorkingDirectory=/spark-git/spark
ExecStartPre=-/usr/bin/docker stop rproxy > /dev/null
ExecStartPre=-/usr/bin/docker rm rproxy > /dev/null
ExecStart=/usr/bin/docker run -it --rm --name rproxy -p 80:80 -d shwsun/rproxy
Restart=never
[Install]
WantedBy=multi-user.target

# Register the Service
systemctl daemon-reload
systemctl enable rproxy
systemctl start rproxy
systemctl status rproxy
```

##  
클러스터 내부 서비스 프락시 사용하기  
아래와 같이 클러스터 내부 ip를 vm host 내부에 등록  
```bash
vi /etc/hosts
172.21.0.2 namenode
172.21.0.3 dn01
172.21.0.4 dn02
172.21.0.5 dn03
```



## 패스워드 인증 추가하기  


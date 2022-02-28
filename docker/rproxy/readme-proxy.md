# Reverse Proxy  
Cluster Web UI 호출에 사용할 proxy 설정  


```bash
# nginx -s reload
docker run -it --name proxy -p 80:80 -d nginx
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

docker run -it --name rproxy -p 80:80 -d shwsun/rproxy

```

## proxy 설정 수정하기 
로컬 파일에서 수정한 설정값을 컨테이너에 직접 반영하는 방법  
```bash
docker cp default.conf rproxy:/etc/nginx/conf.d/default.conf
docker exec -it rproxy nginx -s reload
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



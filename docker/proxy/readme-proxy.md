# Reverse Proxy  
Cluster Web UI 호출에 사용할 proxy 설정  


```bash
docker run -it --name proxy -p 80:80 -d nginx
```

```Dockerfile
FROM nginx
COPY default.conf /etc/nginx/conf.d/default.conf
```

/etc/nginx/conf.d/default.conf 에서 수정해야 

nginx -s reload

```bash
#docker/proxy 
docker build -t shwsun/hdfs-proxy .
docker run -it --name proxy -p 80:80 -d shwsun/hdfs-proxy
```
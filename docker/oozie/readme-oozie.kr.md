# Oozie install in docker  
```bash
cd oozie 
docker build -t shwsun/oozie .

docker run -itd --privileged --name oozie --hostname oozie --rm -p 10000:11000 shwsun/oozie
```


```bash
# oozie 
wget https://dlcdn.apache.org/oozie/5.2.1/oozie-5.2.1.tar.gz
# extJS 2.2  
wget http://archive.cloudera.com/gplextras/misc/ext-2.2.zip  

```
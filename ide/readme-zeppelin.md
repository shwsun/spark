# Zeppelin 
웹 코딩 도구로 zeppelin을 사용할 수 있게 설치합니다.  
  
Docker로 설치하고, 필요 라이브러리나 소스 폴더는 host machine과 volume 공유로 연동합니다.  
  
```bash
docker run -u $(id -u) -p 8080:8080 --rm -v $PWD/logs:/logs -v $PWD/notebook:/notebook \
           -e ZEPPELIN_LOG_DIR='/logs' -e ZEPPELIN_NOTEBOOK_DIR='/notebook' \
           --name zeppelin apache/zeppelin:0.10.0 > /dev/null 2>&1 & 
# docker run -u $(id -u) -p 8080:8080 --rm -v /mnt/disk1/notebook:/notebook \
# -v /usr/lib/spark-current:/opt/spark -v /mnt/disk1/flink-1.12.2:/opt/flink -e FLINK_HOME=/opt/flink  \
# -e SPARK_HOME=/opt/spark  -e ZEPPELIN_NOTEBOOK_DIR='/notebook' --name zeppelin apache/zeppelin:0.10.0
```

---  
# Jupyter scala  
```bash
docker run -it --rm -p 8888:8888 jupyter/all-spark-notebook
# scala kernel 
# https://github.com/jupyter-scala/jupyter-scala almond  
# in jupyter terminal 
curl -Lo coursier https://git.io/coursier-cli
chmod +x coursier
#./coursier launch --fork almond -- --install
./coursier launch --fork almond:0.10.0 --scala 2.12.11 -- --install
rm -f coursier
```
---  
# Jypter Toree scala 
  
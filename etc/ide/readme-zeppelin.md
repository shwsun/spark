# Zeppelin 
웹 코딩 도구로 zeppelin을 사용할 수 있게 설치합니다.  
Spark 코딩 시, jupyter lab 보다 편의성이 떨어지는 것으로 판단.  
  
Docker로 설치하고, 필요 라이브러리나 소스 폴더는 host machine과 volume 공유로 연동합니다.  
  
```bash
docker run -u $(id -u) -p 8080:8080 --rm -v $PWD/logs:/logs -v $PWD/spark-local/notebooks:/notebook \
           -e ZEPPELIN_LOG_DIR='/logs' -e ZEPPELIN_NOTEBOOK_DIR='/notebook' \
           --name zeppelin apache/zeppelin:0.10.0 > /dev/null 2>&1 & 
# docker run -u $(id -u) -p 8080:8080 --rm -v /mnt/disk1/notebook:/notebook \
# -v /usr/lib/spark-current:/opt/spark -v /mnt/disk1/flink-1.12.2:/opt/flink -e FLINK_HOME=/opt/flink  \
# -e SPARK_HOME=/opt/spark  -e ZEPPELIN_NOTEBOOK_DIR='/notebook' --name zeppelin apache/zeppelin:0.10.0
```
  
---  
# Jupyter pyspark simple lab  
커스텀 이미지 shwsun/jupyter-spark   
도커 실행시 바로 주피터 실행되도록 수정해야 함.  
```bash
docker run -itd --privileged --name spark-client --hostname spark-client --rm -v /spark-git/spark/spark-local/notebooks:/notebooks -p 4040-4050:4040-4050 -p 6006:6006 -p 8080:8080 -p 8888:8888 shwsun/jupyter-spark

# --NotebookApp.token='' --NotebookApp.password=''
docker run -itd --privileged --name spark-client --hostname spark-client --rm -p 4040-4050:4040-4050 -p 6006:6006 -p 8080:8080 -p 8888:8888 -v /spark-git/spark/spark-local/notebooks:/notebooks shwsun/jupyter-spark jupyter lab --allow-root --ip='*' --notebook-dir='/notebooks' --workspace='/notebooks' > /dev/null 2>&1 & 
# set JAVA_HOME 빠짐  ... Dockerfile 만드는 중... 
# to view login token
docker exec spark-client jupyter server list 
```
  
---  
# Jupyter scala  
공개 이미지 all-spark 사용  
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
  
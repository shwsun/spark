# Spark in Ubuntu base Docker  

## Jupyter Lab & JDK  
```bash
sudo -i 
mkdir -p /home/vagrant/spark-client
docker pull ubuntu:18.04   
docker run -itd --privileged --name spark-client --hostname spark-client --rm -v /spark-client:/notebooks -p 8888 -p 8080 -p 6006 -p 4040 ubuntu:18.04
docker exec -it spark-client /bin/bash

apt update
# apt install -y python3.8
# rm /usr/bin/python3 
# ln /usr/bin/python3.8 /usr/bin/python3
# ln /usr/bin/python3.8 /usr/bin/python  
apt install -y python3-pip iputils-ping
ln /usr/bin/pip3 /usr/bin/pip  
pip install jupyterlab
# open jdk 8 
apt install -y openjdk-8-jdk 
pip install pyspark

#mkdir /home/jovyan 
jupyter lab --allow-root --ip='*' --NotebookApp.token='' --NotebookApp.password='' --workspace='/notebooks' > /dev/null 2>&1 & 

docker commit spark-client shwsun/jupyter-spark

```


## Run Spark-client image 
remote spark 에 연결하기 위해 docker 를 spark-default bridge로 네트웍 설정해야 한다.  
```bash
docker run -itd --privileged --name spark-client --hostname spark-client --rm -v /home/shwsun/spark/client:/notebooks -p 8888 -p 8080 -p 6006 -p 4040 --gpus all shwsun/jupyter-spark
docker network connect spark_default spark-client
docker exec -it spark-client /bin/bash
jupyter lab --allow-root --ip='*' --NotebookApp.token='' --NotebookApp.password='' --workspace='/tf/notebooks' > /dev/null 2>&1 & 

```

docker run -itd --privileged --name spark-client --hostname spark-client --rm -v C:\Study\spark_env\git-prj\spark\spark-src:/notebooks -p 8888 -p 8080 -p 6006 -p 4040 shwsun/jupyter-spark

docker run -itd --privileged --name spark-client --hostname spark-client --rm -p 8888 -p 8080 -p 6006 -p 4040 shwsun/jupyter-spark

### run spark-client in gcp  
```bash
# export JAVA_HOME, PATH

# /home/coder/spark-prj/spark/spark-src/samples
sudo docker run -itd --privileged --name spark-client --hostname spark-client --rm -p 9999:8888 -p 4040-4050 shwsun/jupyter-spark
sudo docker exec -it spark-client /bin/bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
export PATH=$PATH:/usr/lib/jvm/java-8-openjdk-amd64/bin/
#jupyter lab --allow-root --ip='*' --NotebookApp.token='' --NotebookApp.password='' --workspace='/tf/notebooks' > /dev/null 2>&1 & 
jupyter lab --allow-root --ip='*' --notebook-dir='/tf/notebooks' --workspace='/tf/notebooks' > /dev/null 2>&1 & 

# to join spark-cluster. bitnami docker-compose spark cluster's network name is 'spark_default' 
sudo docker network connect spark_default spark-client
```
  
---  
# install bitnami spark cluster 
```bash
sudo mkdir -p /spark-cluster
sudo -i
cd /spark-cluster
curl -LO https://raw.githubusercontent.com/bitnami/bitnami-docker-spark/master/docker-compose.yml
# default master UI 8080, spark master url : 7077
# need to open gcp port 7077, 8080 
# modify yaml to open 7077
docker-compose up 
```
yaml 에서 4040 등을 열면, spark Job UI 를 연결할 수 있다.  
  
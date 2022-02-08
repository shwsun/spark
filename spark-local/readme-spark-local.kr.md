# Spark Local(minimum install mode) 
Ubuntu base Docker에 필요한 최소 설치만 진행해서 Spark를 사용해 봅니다.  
python 에서는 pyspark 만 설치하면 Spark를 사용할 수 있습니다.  
단, Spark 자체는 JVM에서 작동하기 때문에, JDK는 미리 설치해 두어야 합니다.  
  
빠르게 진행하기 위해 우선 Docker Container에 pyspark를 설치해 두고 이를 이용해 테스트 해 봅니다.  
코딩 도구(IDE)로 사용하기 위한 `Jupyter`도 같이 설치해 둡니다.  
  
앞으로 Spark local coding 시에는 미리 만들어 둔 컨테이너를 실행하기만 하면 `Jupyter`를 통해 spark를 개발할 수 있습니다.  

## Docker container에 pyspark 설치해서 준비해 두기   
아래와 같이 ubuntu container에 파이썬, JDK, pyspark, jupyter를 설치하고 이 컨테이너를 재사용하기 위해 commit 합니다.  
> 향후에 이를 `Dockerfile` script로 재구성할 예정입니다.  
이렇게 구성해 둔 컨테이너는 앞으로 `shwsun/spark-client` 이름으로 불러서 사용합니다.  

```bash
# ubuntu 환경에 pyspark 설치하기 
sudo -i 
mkdir -p /home/vagrant/spark-client
docker pull ubuntu:18.04   
docker run -itd --privileged --name spark-client --hostname spark-client --rm -v /spark-client:/notebooks -p 8888 -p 8080 -p 6006 -p 4040 ubuntu:18.04
# container에서 직접 수동 설치  
docker exec -it spark-client /bin/bash

# python, jupyter 설치  
apt update
# apt install -y python3.8
# rm /usr/bin/python3 
# ln /usr/bin/python3.8 /usr/bin/python3
# ln /usr/bin/python3.8 /usr/bin/python  
apt install -y python3-pip iputils-ping
ln /usr/bin/pip3 /usr/bin/pip  
pip install jupyterlab
# open jdk 8 설치. 향후 hive 등 설치를 고려하면, jdk 8 설치해야 함.  
apt install -y openjdk-8-jdk 
# spark 설치  
pip install pyspark

# jupyter server 실행  
#mkdir /home/jovyan 
jupyter lab --allow-root --ip='*' --NotebookApp.token='' --NotebookApp.password='' --workspace='/notebooks' > /dev/null 2>&1 & 

# 정상 실행 확인 후에 아래와 같이 컨테이너 저장  
docker commit spark-client shwsun/jupyter-spark
# shwsun/jupyter-spark 이름으로 docker hub에 push 해 둔 상태라 앞으로 docker pull shwsun/jupyter-spark 로 사용할 수 있음  

```


## Run Spark-client image  
미리 준비해 둔 `shwsun/jupyter-spark` 이미지를 이용해 spark 개발 환경을 실행합니다.  
```bash
```



## remote cluster에 연결하기  
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
  
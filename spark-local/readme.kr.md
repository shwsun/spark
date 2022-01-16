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

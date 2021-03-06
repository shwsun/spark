# Spark Local(minimum install mode) 
Ubuntu base Docker에 필요한 최소 설치만 진행해서 Spark를 사용해 봅니다.  
python 에서는 pyspark 만 설치하면 Spark를 사용할 수 있습니다.  
단, Spark 자체는 JVM에서 작동하기 때문에, JDK는 미리 설치해 두어야 합니다.  
  
빠르게 진행하기 위해 우선 Docker Container에 pyspark를 설치해 두고 이를 이용해 테스트 해 봅니다.  
코딩 도구(IDE)로 사용하기 위한 `Jupyter`도 같이 설치해 둡니다.  
  
앞으로 Spark local coding 시에는 미리 만들어 둔 컨테이너를 실행하기만 하면 `Jupyter`를 통해 spark를 개발할 수 있습니다.  
  
---  
# 준비해 둔 container 실행하기  
미리 준비해 둔 Virtualbox 또는 GCP의 VM에 연결해서, 해당 machine에서 진행합니다.  
spark local 개발 환경을 밑바닥부터 만드는 방법은 뒤에 설명합니다.  
```bash
# Virtualbox VM으로 진행하는 경우, vm 실행하려면 'spark-local' 경로에서 아래 명령 실행 
# cd spark-local
vagrant up spark-client 
```
  
---  
## Docker container에 pyspark 설치해서 준비해 두기   
재사용 편의를 위해 vm 내부에 spark 개발환경을 직접 설치하지 않고, docker를 이용해 설치합니다.  

- spark 개발환경을 설치할 VM을 `spark-client`라는 이름으로 준비합니다.  
spark-local 경로에 `Vagrantfile` 스크립트 파일(빈 파일)을 생성하고 아래와 같은 내용을 추가합니다.  
```ruby
Vagrant.configure("2") do |config|
    # config.vbguest.auto_update = false
    # 192.168.56.xx 에서 .2x 대역을 spark machine으로 사용할 예정  
    # spark-client 는 .29 번 사용
    # spark-client  
    # spark 개발에 사용할 적당한 메모리와 cpu core를 할당한다.
    # 코드 작성 중인 노트북은 사양이 낮아서 memory 4G, cpu 2 core만 할당했음.  
    config.vm.define "spark-client" do |vname|
        vname.vm.box = "ubuntu"
        vname.vm.hostname = "spark-client"

        vname.trigger.before :halt do |trigger|
            trigger.warn = "graceful shutdown hook"
            trigger.run_remote = {inline: "echo 'test machine is now shutting down'"}
        end

        vname.vm.provider "virtualbox" do |vb|
            vb.name = "test"
            vb.customize ['modifyvm', :id, '--audio', 'none']
            vb.memory = 4000
            vb.cpus = 2
        end
        vname.vm.network "private_network", ip: "192.168.56.29"
    end
end
```
  
- vm 에 연결해서 jdk, python, pyspark, jupyter을 설치합니다.  
```bash
# boot vm 
vagrant up spark-client 
# connect to vm 
vagrant ssh spark-client  

# belows should be proceeded in spark-client console  
```
*** 아래부터는 `spark-client` vm에 연결한 console 에서 실행합니다. ***  

아래와 같이 ubuntu container에 파이썬, JDK, pyspark, jupyter를 설치하고 이 컨테이너를 재사용하기 위해 commit 합니다.  
> 향후에 이를 `Dockerfile` script로 재구성할 예정입니다.  
이렇게 구성해 둔 컨테이너는 앞으로 `shwsun/spark-client` 이름으로 불러서 사용합니다.  

> *** image pull 반복 발생으로 테더링 비용 문제 발생. 아래부터는 gcp vm에서 진행 ***  



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


## Run Spark Local mode 
미리 준비해 둔 `shwsun/jupyter-spark` 이미지를 이용해 spark 개발 환경을 실행합니다.  
```bash
# in vm. /spark-git/spark/spark-local
# 컨테이너 이미지를 실행
docker run -itd --privileged --name spark-client --hostname spark-client --rm -v /spark-git/spark/spark-local:/tf/notebooks -p 8888:8888 -p 4040-4050:4040-4050 shwsun/jupyter-spark
docker exec -it spark-client /bin/bash

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
export PATH=$PATH:/usr/lib/jvm/java-8-openjdk-amd64/bin/
# local vm 에서 실행시에는 본인만 접근하므로 login auth 없는게 편하다
#jupyter lab --allow-root --ip='*' --NotebookApp.token='' --NotebookApp.password='' --notebook-dir='/tf/notebooks' --workspace='/tf/notebooks' > /dev/null 2>&1 & 
# gcp 에서 실행 시에는 다른 사람이 연결 가능하므로, login auth 켜둔다. 
jupyter lab --allow-root --ip='*' --notebook-dir='/tf/notebooks' --workspace='/tf/notebooks' > /dev/null 2>&1 & 
# to get access token 
jupyter server list 
```
> `shwsun/jupyter-spark` 이미지가 아직 완전하지 않아서, 컨테이너 실행 후에 다시 컨테이너 내부에서 주피터를 실행해야 함.  
> 향후에는 컨테이너 실행만으로 pyspark jupyter 가 자동 실행하게 개선할 예정  




## remote cluster에 연결하기  
`spark-client` 외부에 cluster를 실행한 상태에서 spark cluster 에 연결해서 작동하는 `spark cluster client mode`를 실행해 봅니다.  
먼저 미리 만들어 둔 spark cluster를 실행합니다.  
간단하게 bitnami 의 spark용 컨테이너를 이용합니다.  
spark cluster 용 bitnami 컨테이너가 위치한 경로에서 'docker-compose up'를 실행하면 클러스터가 실행됩니다.  
  
remote spark 에 연결하기 위해 spark-client docker 를 spark cluster network에 참여 시켜야 합니다.   
```bash
# spark cluster 실행하기
cd /spark-cluster 
docker-compose up
# spark cluster network 에 참여하기  
docker network connect spark-cluster_default spark-client
```

`spark-client` 를 이용해 `spark-cluster`에 연결하는 스파크 세션을 생성하면 아래와 같은 spark master UI와 app UI를 확인할 수 있다.  
[]()


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
```yaml
Page up
version: '2'
  
services:
  spark:
    image: docker.io/bitnami/spark:3
    environment:
      - SPARK_MODE=master
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
    ports:
            - '8080:8080'
            - '7077:7077'
  spark-worker:
    image: docker.io/bitnami/spark:3
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://34.64.97.16:7077
      - SPARK_WORKER_MEMORY=1G
      - SPARK_WORKER_CORES=1
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
```
yaml 에서 4040 등을 열면, spark Job UI 를 연결할 수 있다.  
  
# Docker 환경 설치하기  
Ubuntu(vm)에 Docker를 설치합니다.  

vagrant ssh test
```bash
sudo -i
apt update  
apt install -y ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io
```
  
# Docker-compose install 
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
  
---  
# pyspark+jupyter 
ubuntu container에 pyspark와 jupyter notebook을 설치  

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
  
---  
# HDFS Single + Hive + Spark  
hdfs cluster를 구성하고 그 위에 hive와 spark를 추가한 container  
  
### 유용한 site  
[Hadoop Single Cluster 설치](https://hadoop.apache.org/docs/r3.2.2/hadoop-project-dist/hadoop-common/SingleCluster.html)  
[Hive wiki] (https://cwiki.apache.org/confluence/display/Hive/Home)
  
각종 설치 파일 다운로드 
```bash
mkdir /install-files
cd /install-files
# spark 3.1.2 
wget https://dlcdn.apache.org/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz
# hadoop 3.2.2 (3.2.0)
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.2.2/hadoop-3.2.2.tar.gz
# hive 2.3.9 (2.3.7) 
wget https://dlcdn.apache.org/hive/hive-2.3.9/apache-hive-2.3.9-bin.tar.gz
```

```bash
sudo -i
docker run -itd --privileged --name spark-hdfs --hostname spark-hdfs --rm ubuntu:18.04
docker exec -it spark-hdfs /bin/bash  
# in spark-hdfs 
apt update 
apt install -y wget 
apt install -y ssh
apt install -y pdsh

mkdir /install-files
cd /install-files
# hadoop 3.2.2 (3.2.0)
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.2.2/hadoop-3.2.2.tar.gz
mkdir /hadoop
tar -xvf hadoop-3.2.2.tar.gz -C /hadoop

# install java 
apt install -y openjdk-8-jdk
# set to the root of your Java installation
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
export PATH=$PATH:/usr/lib/jvm/java-8-openjdk-amd64/bin/
# check hadoop installed
/hadoop/hadoop-3.2.2/bin/hadoop
```
  
### Hadoop Standalone Operation 
```bash
mkdir input
cp etc/hadoop/*.xml input
bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.2.jar grep input output 'dfs[a-z.]+'
cat output/*
```
  
### Pseudo-Distributed Operation  
etc/hadoop/core-site.xml:
```xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
```
  
etc/hadoop/hdfs-site.xml:
```xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
</configuration>
```
  
```bash
cat <<EOF|tee /hadoop/hadoop-3.2.2/etc/hadoop/core-site.xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
EOF

cat <<EOF|tee /hadoop/hadoop-3.2.2/etc/hadoop/hdfs-site.xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
</configuration>>
EOF
```
  
#### Setup passphraseless ssh  
```bash
ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys

sudo /etc/init.d/ssh start
ssh -o StrictHostKeyChecking=no localhost
```
#### Execution
```bash
cd /hadoop/hadoop-3.2.2
# 1. Format the filesystem: 
bin/hdfs namenode -format
# 2. Start NameNode daemon and DataNode daemon:
sbin/start-dfs.sh
# 3. Browse the web interface for the NameNode
#  http://localhost:9870/
# 4. Make the HDFS directories required to execute MapReduce jobs:
bin/hdfs dfs -mkdir /user
bin/hdfs dfs -mkdir /user/<username>
# 5. Copy the input files into the distributed filesystem:
bin/hdfs dfs -mkdir input
bin/hdfs dfs -put etc/hadoop/*.xml input
# 6. Run some of the examples provided:
bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.2.jar grep input output 'dfs[a-z.]+'
# 7. Examine the output files: 
#  Copy the output files from the distributed filesystem to the local filesystem and examine them:
bin/hdfs dfs -get output output
cat output/*
# 7. or View the output files on the distributed filesystem:
bin/hdfs dfs -cat output/*
# 8. When you're done, stop the daemons with:
sbin/stop-dfs.sh
```

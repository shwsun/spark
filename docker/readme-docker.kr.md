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
  
# docker login error X11 
```bash
apt-get remove -y golang-docker-credential-helpers
```
  
---  
# pyspark+jupyter 
ubuntu container에 pyspark와 jupyter notebook을 직접 설치  
뒤에서 이를 다시 `Dockerfile` 스크립트로 전환한다.  

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
  
## jupyter-spark Dockerfile  
spark를 실행/연결하고 jupyter notebook을 이용해 코딩할 수 있는 최소 환경을 아래와 같이 설치합니다.  
도커 이미지를 만들기 위한 스크립트는 `./jupyter-spark` 경로를 참고합니다.  
- python3  
- open jdk 8  
- pyspark  
- jupyter lab  
아래와 같이 `shwsun/jupyter-spark` 컨테이너를 실행하면 jupyter notebook이 `8888` 포트로 실행됩니다.  
```bash
docker run -itd --privileged --name spark-client --hostname spark-client --rm -p 8888:8888 -p 4040-4050:4040-4050 -v /spark-git/spark/spark-local/notebooks:/notebooks shwsun/jupyter-spark:1.0  
# token 확인 
docker exec -it spark-client jupyter server list
```
  
> ## Docker image 만들기  
```bash
WORK_ROOT=/spark-git/spark
cd $WORK_ROOT
docker build -t shwsun/jupyter-spark:1.0 docker/jupyter-spark/
```
>
  
---  
# HDFS Single + Hive + Spark  
hdfs cluster를 구성하고 그 위에 hive와 spark를 추가한 container 를 구성한다.  
  
ubuntu에 hadoop single cluster를 구성하는 순서는 아래와 같습니다.  
1. ubuntu container 
2. ubuntu apt repo 설정 및 필수 package 설치 - ssh 관련 
3. jdk 설치  
4. hadoop 설치 : 패키지 다운로드 및 압축 해제  
5. hadoop 작동 확인 : standalone, pseudo distribution, pseudo distribution(Yarn)  
  


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

# install java 
apt install -y openjdk-8-jdk
# set to the root of your Java installation
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
export PATH=$PATH:/usr/lib/jvm/java-8-openjdk-amd64/bin/

# hadoop 설치 파일 준비  
mkdir /install-files
cd /install-files
# hadoop 3.2.2 (3.2.0)
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.2.2/hadoop-3.2.2.tar.gz
mkdir /hadoop
tar -xvf hadoop-3.2.2.tar.gz -C /hadoop
# check hadoop installed
/hadoop/hadoop-3.2.2/bin/hadoop


cat <<EOF|tee shells/install-hadoop-single.sh
sudo -i
# in spark-hdfs 
apt update 
apt install -y wget 
apt install -y ssh
apt install -y pdsh

# install java 
apt install -y openjdk-8-jdk
# set to the root of your Java installation
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
export PATH=$PATH:/usr/lib/jvm/java-8-openjdk-amd64/bin/

# hadoop 설치 파일 준비  
mkdir /install-files
cd /install-files
# hadoop 3.2.2 (3.2.0)
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.2.2/hadoop-3.2.2.tar.gz
mkdir /hadoop
tar -xvf hadoop-3.2.2.tar.gz -C /hadoop
# check hadoop installed
/hadoop/hadoop-3.2.2/bin/hadoop
EOF
```
```bash
chmod 755 shells/install-hadoop-single.sh
shells/install-hadoop-single.sh  

```
  
### Hadoop Standalone Operation 
```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
export HADOOP_HOME=/hadoop/hadoop-3.2.2
cd $HADOOP_HOME
mkdir input
cp etc/hadoop/*.xml input
bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.2.jar grep input output 'dfs[a-z.]+'
cat output/*
# rm -rdf input output
```
  
### Pseudo-Distributed Operation  
env var setting 
```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
export HADOOP_HOME=/hadoop/hadoop-3.2.2
```

etc/hadoop/core-site.xml, etc/hadoop/hdfs-site.xml:
```bash
# init-pseudo-setting.sh
HADOOP_HOME=/hadoop/hadoop-3.2.2
cat <<EOF|tee $HADOOP_HOME/etc/hadoop/core-site.xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
EOF

cat <<EOF|tee $HADOOP_HOME/etc/hadoop/hdfs-site.xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
</configuration>
EOF

echo "[core-site, hdfs-site] setting for Pseudo-Distributed mode completed"
```
  
#### Setup passphraseless ssh  
```bash
# start ssh 
cat <<EOF|tee shells/init-ssh.sh
#ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
echo -e 'y\n' | ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys

#sudo /etc/init.d/ssh start
/etc/init.d/ssh start
ssh -o StrictHostKeyChecking=no local
chmod 755 shells/init-ssh.sh
shells/init-ssh.sh
```
#### Execution
settings to start name node as root 
```bash
# in hadoop-env.sh  
cat <<EOF |tee $HADOOP_HOME/etc/hadoop/hadoop-env.sh
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
export HADOOP_HOME=/hadoop/hadoop-3.2.2
export HADOOP_OS_TYPE=${HADOOP_OS_TYPE:-$(uname -s)}

export HDFS_NAMENODE_USER=root
export HDFS_DATANODE_USER=root
export HDFS_SECONDARYNAMENODE_USER=root
export YARN_RESOURCEMANAGER_USER=root
export YARN_NODEMANAGER_USER=root

export PDSH_RCMD_TYPE=ssh
EOF


# $HADOOP_HOME/libexec/hadoop-functions.sh:
PDSH_RCMD_TYPE=ssh PDSH_SSH_ARGS_APPEND="${HADOOP_SSH_OPTS}" pdsh \

# I fixed this problem for hadoop 3.1.0 by adding
# PDSH_RCMD_TYPE=ssh
# in my .bashrc as well as $HADOOP_HOME/etc/hadoop/hadoop-env.sh
```
```bash
cd $HADOOP_HOME
# 1. Format the filesystem: 
bin/hdfs namenode -format
# 2. Start NameNode daemon and DataNode daemon:
sbin/start-dfs.sh
# 3. Browse the web interface for the NameNode
#  http://localhost:9870/
# 4. Make the HDFS directories required to execute MapReduce jobs:
bin/hdfs dfs -mkdir /user
bin/hdfs dfs -mkdir /user/root
# 5. Copy the input files into the distributed filesystem:
bin/hdfs dfs -mkdir input
bin/hdfs dfs -mkdir output
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
  
> docker commit spark-hdfs shwsun/hdfs:single  
> docker login -u shwsun -p xxxx
> docker push shwsun/hdfs

---  
### YARN on a Single Node 
assume that ~ 'Make the HDFS directories' instructions are already executed.  
#### Configure parameters  

mapred, 
```bash
# etc/hadoop/mapred-site.xml:
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/*:$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/lib/*</value>
    </property>
</configuration>

# etc/hadoop/yarn-site.xml:  
<configuration>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.env-whitelist</name>
        <value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PREPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_MAPRED_HOME</value>
    </property>
</configuration>
```
```bash
# Start ResourceManager daemon and NodeManager daemon: 
sbin/start-yarn.sh
# Browse the web interface for the ResourceManager; by default it is available at:
# ResourceManager - http://localhost:8088/

# Run a MapReduce job. ...

# stop the daemons with:
sbin/stop-yarn.sh
```


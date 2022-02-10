#! install-hadoop-single.sh 
# in spark-hdfs 
sudo -i 
apt update 
apt install -y wget 
apt install -y ssh
apt install -y pdsh

# install java 
apt install -y openjdk-8-jdk
# set to the root of your Java installation
# need to move export sentence into .bashrc to share this env var setting 
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
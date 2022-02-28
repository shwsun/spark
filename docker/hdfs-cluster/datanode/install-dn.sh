# install-nn.sh 
# in spark-hdfs 
# sudo -i 
apt-get update 
apt-get install -y wget ssh pdsh
# apt install -y ssh
# apt install -y pdsh

# install java 
apt-get install -y openjdk-8-jdk
# set to the root of your Java installation
# need to move export sentence into .bashrc to share this env var setting 
# JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
# PATH=$PATH:/usr/lib/jvm/java-8-openjdk-amd64/bin/

# hadoop 설치 파일 준비  
# mkdir /install-files
# cd /install-files
# hadoop 3.2.2 (3.2.0)
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.2.2/hadoop-3.2.2.tar.gz
tar -xvf hadoop-3.2.2.tar.gz -C /
mv /hadoop-3.2.2 /hadoop
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=/hadoop
export PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
cat <<EOF |tee -a ~/.bashrc
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=$HADOOP_HOME
export PATH=\$PATH:\$JAVA_HOME/bin:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin
EOF
# check hadoop installed
# /hadoop/hadoop-3.2.2/bin/hadoop


#### HDFS cluster mode namenode setting ####  
cp /install-files/conf/*.xml $HADOOP_HOME/etc/hadoop/

echo "[core-site, hdfs-site] setting for Pseudo-Distributed mode completed"



# in hadoop-env.sh  
cat <<EOF |tee $HADOOP_HOME/etc/hadoop/hadoop-env.sh
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
export HADOOP_HOME=$HADOOP_HOME
export HADOOP_OS_TYPE=${HADOOP_OS_TYPE:-$(uname -s)}
export HDFS_NAMENODE_USER=root
export HDFS_DATANODE_USER=root
export HDFS_SECONDARYNAMENODE_USER=root
export YARN_RESOURCEMANAGER_USER=root
export YARN_NODEMANAGER_USER=root
export PDSH_RCMD_TYPE=ssh
EOF

cat <<EOF |tee $HADOOP_HOME/etc/hadoop/workers
dn01
dn02
dn03

EOF
# start ssh 
mkdir -p /shells
cat <<EOF |tee /shells/init-ssh.sh
#ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
echo -e 'y\n' | ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
# mkdir -p ~/.ssh
# cp /install-files/authorized_keys ~/.ssh/authorized_keys

chmod 0600 ~/.ssh/authorized_keys
# /etc/init.d/ssh start
EOF

echo "---- HDFS configuration completed. ----"
chmod 755 /shells/init-ssh.sh
/shells/init-ssh.sh
echo "---- HDFS SSH connection completed. ----"
# $HADOOP_HOME/bin/hdfs namenode -format
echo "---- HDFS Starting ... ----"
# $HADOOP_HOME/sbin/start-dfs.sh
# $HADOOP_HOME/bin/hdfs --daemon start datanode
# echo "---- HDFS Datanode Started. ----"
# $HADOOP_HOME/bin/yarn --daemon start nodemanager
# echo "---- HDFS Nodemanager Started. ----"


# hdfs dfs -mkdir /user
# hdfs dfs -mkdir /user/root

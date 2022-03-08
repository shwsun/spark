# 
export HIVE_VER=3.1.2 
wget https://dlcdn.apache.org/hive/hive-${HIVE_VER}/apache-hive-${HIVE_VER}-bin.tar.gz
mkdir /hive-bin
tar -xvf apache-hive-${HIVE_VER}-bin.tar.gz -C /
mv /apache-hive-${HIVE_VER}-bin /hive-bin

cat <<EOF |tee -a ~/.bashrc
export HIVE_HOME=/hive-bin
export PATH=\$PATH:\$HIVE_HOME/bin
EOF
#source ~/.bashrc
export HIVE_HOME=/hive-bin
export PATH=$PATH:$HIVE_HOME/bin
export HADOOP_HOME=/hadoop
echo "HADOOP_HOME=$HADOOP_HOME"
# 1. hive-env.sh 설정 파일
echo "HADOOP_HOME=$HADOOP_HOME" > $HIVE_HOME/conf/hive-env.sh
# 2. hive-site.xml 설정 : {{hostname}} 을 실제 host name으로 치환  
cp /install-files/conf-hive/hive-site.xml $HIVE_HOME/conf/
sed -i 's/{{hostname}}/${hostname}/' $HIVE_HOME/conf/hive-site.xml 
# 5. guava version 맞추기    
rm $HIVE_HOME/lib/guava-19.0.jar
cp $HADOOP_HOME/share/hadoop/hdfs/lib/guava-27.0-jre.jar $HIVE_HOME/lib
# 6. jdbc driver classpath 등록  
cd /install-files
wget https://downloads.mysql.com/archives/get/p/3/file/mysql-connector-java-5.1.49.tar.gz
tar -zxvf mysql-connector-java-5.1.49.tar.gz
cp mysql-connector-java-5.1.49/mysql-connector-java-5.1.49-bin.jar $HIVE_HOME/lib/
#popd 
echo "==== Hive installation completed. ===="
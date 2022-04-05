cd /install-files
# 1. download spark without hadoop
#wget https://dlcdn.apache.org/spark/spark-3.1.3/spark-3.1.3-bin-without-hadoop.tgz
wget https://dlcdn.apache.org/spark/spark-3.2.1/spark-3.2.1-bin-without-hadoop.tgz
# 2. unzip to spark home dir 
tar -xvf spark-3.2.1-bin-without-hadoop.tgz -C /
mv /spark-3.2.1-bin-without-hadoop /spark
# 3. env variables setting
cat <<EOF |tee -a ~/.bashrc
export SPARK_HOME=/spark
export SPARK_DIST_CLASSPATH=\$(hadoop classpath)
export PATH=\$PATH:\$JAVA_HOME/bin:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin:\$HIVE_HOME/bin:\$SPARK_HOME/bin:/usr/local/bin
EOF
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=/hadoop
export SPARK_HOME=/spark
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HADOOP_HOME/lib/native
export PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin:/usr/local/bin
export SPARK_DIST_CLASSPATH=$(hadoop classpath)

# 4. default conf setting
# cd $SPARK_HOME/conf
# cp spark-defaults.conf.template spark-defaults.conf
# cp spark-env.sh.template spark-env.sh
# cp log4j.properties.template log4j.properties
# vi => log4j.rootCategory=WARN, console

# 5. slaves setting 
cp /install-files/conf-spark/* $SPARK_HOME/conf/
mkdir -p /usr/local/spark/eventLog

# spark jdbc driver 복사 . spark jdbc 연결 위해 
cp /install-files/lib/mysql-connector-java-5.1.49/mysql-connector-java-5.1.49-bin.jar $SPARK_HOME/jars/
# 
# 6. 실행 
# > $SPARK_HOME/sbin/start-all.sh
# > $SPARK_HOME/sbin/start-history-server.sh
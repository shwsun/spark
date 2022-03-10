export HADOOP_HOME=/hadoop
export SPARK_HOME=/spark
export LIVY_HOME=/spark-livy
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop

apt-get install -y unzip 
wget https://dlcdn.apache.org/incubator/livy/0.7.1-incubating/apache-livy-0.7.1-incubating-bin.zip 
unzip apache-livy-0.7.1-incubating-bin.zip 
mv ./apache-livy-0.7.1-incubating-bin $LIVY_HOME/
ech "==== Spark Livy server installed. ===="
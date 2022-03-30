# start jupyter 
echo "==== Jupyter JAVA_HOME, PATH env ===="
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=/hadoop
export SPARK_HOME=/spark
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin
echo $PATH
echo "==== Jupyter starting... ===="
jupyter lab --LabApp.max_buffer_size=1048576000 --allow-root --ip='*' --notebook-dir='/notebooks' --workspace='/notebooks' > /dev/null 2>&1 &
sleep 5
echo "==== Jupyter started. ===="
echo | jupyter server list  

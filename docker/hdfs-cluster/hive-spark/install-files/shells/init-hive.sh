#### run hive 
#export HIVE_VER=3.1.2 
export HIVE_HOME=/hive-bin
export HADOOP_EXE_HOME=/hadoop/bin

# 6. init schema 
echo "---- Ready to init schama ----"

$HIVE_HOME/bin/schematool -dbType mysql -initSchema 

#$HIVE_HOME/bin/hive --service metastore 
echo "---- hive schema inited. ----"
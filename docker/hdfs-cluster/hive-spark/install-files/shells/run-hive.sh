#### run hive 
#export HIVE_VER=3.1.2 
export HIVE_HOME=/hive-bin
export HADOOP_EXE_HOME=/hadoop/bin

# 6. init schema 
echo "---- Ready to start hive ----"
## 리모트 방식 
# 3. 하이브용 디렉토리 생성 및 확인 
$HADOOP_EXE_HOME/hdfs dfs -mkdir -p /user/hive/warehouse
$HADOOP_EXE_HOME/hdfs dfs -ls -R /user/hive
# hue 기본 계정용 
$HADOOP_EXE_HOME/hdfs dfs -mkdir -p /user/root
# 4. 쓰기 권한 추가 및 확인  
$HADOOP_EXE_HOME/hdfs dfs -chmod g+w /user/hive/warehouse
$HADOOP_EXE_HOME/hdfs dfs -ls -R /user/hive
$HADOOP_EXE_HOME/hdfs dfs -chmod g+w /user/root
# #$HIVE_HOME/bin/schematool -dbType mysql -initSchema -userName hive -passWord hive
# $HIVE_HOME/bin/schematool -dbType mysql -initSchema 
# 7. hive 서버 실행  
$HIVE_HOME/bin/hiveserver2
#$HIVE_HOME/bin/hive --service metastore 
echo "---- hiveserver2 started ----"
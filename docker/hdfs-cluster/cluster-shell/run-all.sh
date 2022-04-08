# rm -rdf /hdfs/
# echo "==== /hdfs/ cleared. ===="
# docker-compose up
# hdfs/data 와 namenode:/knownhosts 삭제하고 실행해야 한다. 
# knownetworks 삭제 
./sync_key.sh
# Hue start 
echo "====  ssh key synched. ===="

#### node start ####
# init namenode 
echo "====>  Namenode initializing ... <===="
echo "====  formatting ===="
if [ "$1" == "init" ] 
then 
    # rdb init  
    docker exec -it --privileged -u root -d rdb /bin/bash /install-files/shells/init-db.sh
    sleep 10
    echo ">> hive & hue db created. "
    echo ">> namenode inited. "
    # 이미 docker 에서 mount 된 이후라, 지우려면 내용만 지워야 한다.  
    #rm -rdf /hdfs/
    docker exec -u root -it namenode /hadoop/bin/hdfs namenode -format -force
else 
    echo ">> run previously formatted namenode. "
fi



# run hue in detached mode 
docker exec -it --privileged -u root -d hue ./startup.sh  
sleep 5
echo "====>  Hue started. <===="

echo "====  start hdfs ===="
docker exec -u root -it namenode /hadoop/sbin/start-dfs.sh 
echo "====  check namenode process ===="
docker exec -u root -it namenode jps
echo "====  check datanode process ===="
docker exec -u root -it dn01 jps
echo "==== hdfs started. ===="
# yarn start
echo "====>  Yarn initializing ... <===="
docker exec -u root -it namenode /hadoop/sbin/start-yarn.sh 
#$HADOOP_HOME/bin/mapred --daemon start historyserver
echo "====  check namenode process ===="
docker exec -u root -it namenode jps
echo "====  check datanode process ===="
docker exec -u root -it dn01 jps
# yarn hitory server : 19888
echo "====  start job history server ===="
docker exec -u root -it namenode /hadoop/bin/mapred --daemon start historyserver
echo "====  check namenode(jobhistory node) process ===="
docker exec -u root -it namenode jps
echo "====>  Yarn initialized. <===="
# run hiveserver2 in dn01 as detached mode 
if [ "$1" == "init" ] 
then 
    echo ">> hive schema inited. "
    docker exec -it -d dn01 /bin/bash /install-files/shells/init-hive.sh
else 
    echo ">> run previously formatted namenode. "
fi
echo "====>  Start Run Hiveserver2 in dn01 <===="
docker exec -it -d dn01 /bin/bash /install-files/shells/run-hive.sh
echo "====>  Hiveserver2 started. <===="
echo "====>  Start Spark master & History server in spark-master <===="
docker exec -it -d spark-master /bin/bash /install-files/shells/run-spark.sh
docker exec -u root -it spark-master jps
echo "====> Spark master & History server started. <===="

echo "====> Spark Livy server not started. need higher scala build. <===="
# spark 3 scala 1.2 빌드 필요해서 비활성화 
# echo "====>  Start Spark Livy server <===="
# docker exec -it -d spark-master /bin/bash /install-files/shells/run-livy.sh
# docker exec -u root -it spark-master jps
# echo "====> Spark Livy server started. <===="
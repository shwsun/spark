# rm -rdf /hdfs/
# echo "==== /hdfs/ cleared. ===="
# docker-compose up
# hdfs/data 와 namenode:/knownhosts 삭제하고 실행해야 한다. 
# knownetworks 삭제 
./restart-sync_key.sh
# Hue start 
echo "====  ssh key synched. ===="
# run hue in detached mode 
docker exec -it --privileged -u root -d hue ./startup.sh  
sleep 5
echo "====>  Hue started. <===="
#### node start ####
# init namenode 
echo "====>  Namenode initializing ... <===="
echo "====  formatting ===="
docker exec -u root -it namenode /hadoop/bin/hdfs namenode -format -force
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
echo "====>  Start Run Hiveserver2 in dn01 <===="
docker exec -it -d dn01 /bin/bash /install-files/run-hive.sh
echo "====>  Hiveserver2 started. <===="

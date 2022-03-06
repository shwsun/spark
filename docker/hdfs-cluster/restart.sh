# rm -rdf /hdfs/
# echo "==== /hdfs/ cleared. ===="
# docker-compose up
# hdfs/data 와 namenode:/knownhosts 삭제하고 실행해야 한다. 
# knownetworks 삭제 
./sync_key_after_up.sh
# node start 
echo "====  ssh key synched. ===="
docker exec -u root -it namenode /hadoop//bin/hdfs namenode -format -force
docker exec -u root -it namenode /hadoop/sbin/start-dfs.sh 
docker exec -u root -it namenode jps
docker exec -u root -it dn01 jps
echo "==== dfs started. ===="
# yarn start
docker exec -u root -it namenode /hadoop/sbin/start-yarn.sh 
#$HADOOP_HOME/bin/mapred --daemon start historyserver
docker exec -u root -it namenode jps
docker exec -u root -it dn01 jps
# yarn hitory server : 19888
docker exec -u root -it namenode /hadoop/bin/mapred --daemon start historyserver
docker exec -u root -it namenode jps
if [ "$1" == "init" ] 
then
    rm -rdf /hdfs/
    rm -rdf /data/mysql 
    #mkdir -p /data/mysql 
    echo "==== /hdfs/ cleared. ===="
else 
    echo ">> hdfs reused. "
fi

docker-compose down
docker-compose up & 
# need enough time to create dn01~dnn container. 
sleep 30
./run-all.sh init 

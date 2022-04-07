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
sleep 5
./run-all.sh  
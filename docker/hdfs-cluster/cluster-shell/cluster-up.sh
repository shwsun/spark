if [ "$1" == "init" ] 
then
    rm -rdf /hdfs/
    echo "==== /hdfs/ cleared. ===="
else 
    echo ">> hdfs reused. "
fi

docker-compose down
docker-compose up 
if [ "$1" == "init" ] 
    rm -rdf /hdfs/
    echo "==== /hdfs/ cleared. ===="
then 
    echo ">> hdfs reused. "

docker-compose down
docker-compose up 
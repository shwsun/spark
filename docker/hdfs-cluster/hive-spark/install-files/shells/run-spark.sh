# 6. 실행 
SPARK_HOME=/spark
# disable standalone cluster run so to use yarn cluster  
echo "====>  ignore standalone cluster. <===="
# run spark standalone cluster 
# $SPARK_HOME/sbin/start-all.sh
# echo "====>  spark cluster started. <===="
$SPARK_HOME/sbin/start-history-server.sh
echo "====>  spark history server started. <===="
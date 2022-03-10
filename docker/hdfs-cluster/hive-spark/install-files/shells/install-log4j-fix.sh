echo "====> find log4j vulnerabilities. <===="
find / -name "log4j*" |grep -i log4j-
# hive 경로의 log4j 최신 버전으로 덮어쓰기  
# /hive-bin/apache-hive-3.1.2-bin/lib/log4j-slf4j-impl-2.10.0.jar -> log4j-slf4j-impl-2.17.2.jar
# /hive-bin/apache-hive-3.1.2-bin/lib/log4j-core-2.10.0.jar -> log4j-core-2.17.2.jar
# /hive-bin/apache-hive-3.1.2-bin/lib/log4j-api-2.10.0.jar -> log4j-api-2.17.2.jar
# /hive-bin/apache-hive-3.1.2-bin/lib/log4j-web-2.10.0.jar -> log4j-web-2.17.2.jar
# /hive-bin/apache-hive-3.1.2-bin/lib/log4j-1.2-api-2.10.0.jar -> log4j-1.2-api-2.17.2.jar  
# https://dlcdn.apache.org/logging/log4j/2.17.2/apache-log4j-2.17.2-bin.tar.gz
export HIVE_HOME=/hive-bin
cd $HIVE_HOME/lib
rm -rdf log4j-*.jar  
cp /install-files/log4j-fix/*.jar ./ 
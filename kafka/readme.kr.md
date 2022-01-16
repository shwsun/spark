
```bash
vi /etc/hosts

0.0.0.0 kafka1  
192.168.57.3 kafka2
192.168.58.3 kafka3

# 방화벽 해제 및 카프카용 포트 개방 
# 주키퍼 설치 
tar zxf zookeeper-3.4.12.tar.gz 
ln -s zookeeper-3.4.12 zookeeper
mkdir -p /data
#(1: kafka1, 2: kafka2, 3: kafka3)
echo 1 > data/myid 
```
설정파일을 만들자. zookeeper/conf 안에 zoo_sample.cfg가 있으니 zoo.cfg로 복사해서 사용하자.

cd zookeeper/conf
cp zoo_sample.cfg zoo.cfg
vi zoo.cfg

아래 처럼 주석을 풀고 추가작성을 하도록 한다. 3개의 서버에 모두 같은 설정이다.

```bash
# The number of milliseconds of each tick
tickTime=2000
# The number of ticks that the initial
# synchronization phase can take
initLimit=10
# The number of ticks that can pass between
# sending a request and getting an acknowledgement
syncLimit=5
# the directory where the snapshot is stored.
# do not use /tmp for storage, /tmp here is just
# example sakes.
#dataDir=/tmp/zookeeper
dataDir=/home/ykkim/data

# the port at which the clients will connect
clientPort=2181
# the maximum number of client connections.
# increase this if you need to handle more clients
maxClientCnxns=60
#
# Be sure to read the maintenance section of the
# administrator guide before turning on autopurge.
#
# http://zookeeper.apache.org/doc/current/zookeeperAdmin.html#sc_maintenance
#
# The number of snapshots to retain in dataDir
#autopurge.snapRetainCount=3
# Purge task interval in hours
# Set to "0" to disable auto purge feature
#autopurge.purgeInterval=1
server.1=kafka1:2888:3888
server.2=kafka2:2888:3888
server.3=kafka3:2888:3888
```  

이제 실행시켜보자.

./zookeeper/bin/zkServer.sh start
정상적이라면 아래처럼 메시지가 출력된다.

ZooKeeper JMX enabled by default
Using config: /home/ykkim/zookeeper/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED

./zookeeper/bin/zkServer.sh stop

zookeeper-server.service라는 스크립트를 만들고 서비스에 등록하자(root작업)

```bash
 vi /etc/systemd/system/zookeeper.service
[Unit]
Description=zookeeper
After=network.target

[Service]
Type=forking
User=ykkim
Group=ykkim
SyslogIdentifier=zookeeper
WorkingDirectory=/home/ykkim/zookeeper
Restart=always
RestartSec=0s
ExecStart=/home/ykkim/zookeeper/bin/zkServer.sh start
ExecStop=/home/ykkim/zookeeper/bin/zkServer.sh stop

[Install]
WantedBy=multi-user.target
```  


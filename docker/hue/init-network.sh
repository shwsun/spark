# 0. 네트웍 설정  
cat <<EOF |tee -a /etc/hosts
172.17.0.3 namenode  
172.17.0.3 hive-server  
172.17.0.2 rdb
172.17.0.3 meta
EOF
apt-get update 
apt-get install -y net-tools 
apt-get install -y vim 
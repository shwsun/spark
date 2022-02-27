# 0. 네트웍 설정  
cat <<EOF |tee -a /etc/hosts
172.17.0.2 namenode
172.17.0.3 datanode    
172.17.0.4 rdb
172.17.0.5 hue
EOF
apt-get update 
apt-get install -y net-tools 
apt-get install -y vim 
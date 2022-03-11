# install-mysql.sh 
apt-get update 
#apt-get install -y wget 
# mysql 
apt-get install -y mysql-server
sed -i 's/bind-address/bind-address = 0.0.0.0 #/' /etc/mysql/mysql.conf.d/mysqld.cnf
echo "==== install mysql-server ===="
#service mysql start
#service mysql restart

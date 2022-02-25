# install-mysql.sh 
apt-get update 
apt-get install -y wget 
# mysql 
apt-get install -y mysql-server
service mysql start
#service mysql restart

cat <<EOF |tee /install-files/metastore-creation.sh
install plugin validate_password soname 'validate_password.so';
set global validate_password_policy=LOW;
set global validate_password_length=4;
CREATE USER 'hive'@'%' IDENTIFIED BY 'hive';

CREATE DATABASE metastore;
GRANT ALL privileges on *.* to 'hive'@'%' with GRANT option;
flush privileges;
EOF

mysql -u root -p"\n" < /install-files/metastore-creation.sh

# vi /etc/mysql/mysql.conf.d/mysqld.cnf
# bind-address 0.0.0.0

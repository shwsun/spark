# install-mysql.sh 
apt-get update 
#apt-get install -y wget 
# mysql 
apt-get install -y mysql-server
sed -i 's/bind-address/bind-address = 0.0.0.0 #/' /etc/mysql/mysql.conf.d/mysqld.cnf
service mysql start
#service mysql restart

#### create hive meta-store ####
cat <<EOF |tee /install-files/metastore-creation.sh
install plugin validate_password soname 'validate_password.so';
set global validate_password_policy=LOW;
set global validate_password_length=4;
CREATE USER 'hive'@'%' IDENTIFIED BY 'hive';

CREATE DATABASE metastore;
GRANT ALL privileges on *.* to 'hive'@'%' with GRANT option;
flush privileges;
EOF
#mysql -u root -p"\n" < /install-files/metastore-creation.sh

#### create hue db ####
cat <<EOF |tee /install-files/hue_db-creation.sh
install plugin validate_password soname 'validate_password.so';
set global validate_password_policy=LOW;
set global validate_password_length=4;
CREATE USER 'hue_u'@'%' IDENTIFIED BY 'hue_pwd';

CREATE DATABASE hue_db;
GRANT ALL privileges on *.* to 'hue_u'@'%' with GRANT option;
flush privileges;
EOF
mysql -u root -p"\n" < /install-files/hue_db-creation.sh
echo "===== hue_db created. ====="
# vi /etc/mysql/conf.d/mysqld.cnf
# bind-address 0.0.0.0

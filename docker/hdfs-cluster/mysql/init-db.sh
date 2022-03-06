#### create hive meta-store ####
mysql -u root -p"\n" -e "install plugin validate_password soname 'validate_password.so';"
cat <<EOF |tee /install-files/metastore-creation.sql
set global validate_password_policy=LOW;
set global validate_password_length=4;
CREATE USER 'hive'@'%' IDENTIFIED BY 'hive';

CREATE DATABASE metastore;
GRANT ALL privileges on metastore.* to 'hive'@'%' with GRANT option;
flush privileges;
EOF
mysql -u root -p"\n" < /install-files/metastore-creation.sql
echo "===== metastore created. ====="

#### create hue db ####
cat <<EOF |tee /install-files/hue_db-creation.sql
set global validate_password_policy=LOW;
set global validate_password_length=4;
CREATE USER 'hue_u'@'%' IDENTIFIED BY 'hue_pwd';

CREATE DATABASE hue_db;
GRANT ALL privileges on *.* to 'hue_u'@'%' with GRANT option;
flush privileges;
EOF
mysql -u root -p"\n" < /install-files/hue_db-creation.sql
echo "===== hue_db created. ====="
# vi /etc/mysql/conf.d/mysqld.cnf
# bind-address 0.0.0.0
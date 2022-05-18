chown -R mysql:mysql /var/lib/mysql 
service mysql start
sleep 5
echo ">> mysql service started. "
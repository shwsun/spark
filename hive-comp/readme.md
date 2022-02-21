docker-compose up  



docker exec -it hive-server /bin/bash  
cd /employee  
hive -f employee_table.hql  

hadoop fs -put employee.csv   

# validate install  

cd /employee  
hive  
show databases;
use testdb;
select * from employee;

# Oozie install  

## maven latest install 
```bash
wget https://www-us.apache.org/dist/maven/maven-3/3.6.0/binaries/apache-maven-3.6.0-bin.tar.gz -P /tmp
tar xf /tmp/apache-maven-*.tar.gz -C /opt
ln -s /opt/apache-maven-3.6.0 /opt/maven  

nano /etc/profile.d/maven.sh
# /etc/profile.d/maven.sh
export JAVA_HOME=/usr/lib/jvm/default-java
export M2_HOME=/opt/maven
export MAVEN_HOME=/opt/maven
export PATH=${M2_HOME}/bin:${PATH}

chmod +x /etc/profile.d/maven.sh
source /etc/profile.d/maven.sh
```


docker 내부에서 빌드 시, pluginRepository가 proxy 문제로 정상 해결 안 될 수 있다.  
외부에서 빌드 후 빌드 결과만 옮긴다.  

- http://archive.apache.org/dist/oozie/5.2.0/oozie-5.2.0.tar.gz
- tar 압축 해제  
- pom 파일 수정. 클라우데라 url 제거. hadoop 등 버전 변경  
- bin/mkdistro.sh -DskipTests  
- https://oozie.apache.org/docs/5.2.1/ENG_Building.html  

### in spark-master  
docker exec -it spark-master /bin/bash  
```bash
wget http://archive.apache.org/dist/oozie/5.2.0/oozie-5.2.0.tar.gz
tar -xvf oozie-5.2.0.tar.gz 
mv oozie-5.2.0/ /oozie/
cd /oozie  
# modify pom.xml  
apt-get install -y maven  
bin/mkdistro.sh -DskipTests  

```

### in rdb  
using mysql cmd line  
```sql
set global validate_password_policy=LOW;
set global validate_password_length=3;
CREATE USER 'oozie_u'@'%' IDENTIFIED BY 'oozie_pwd';
CREATE DATABASE oozie;
GRANT ALL privileges on oozie.* to 'oozie_u'@'%' with GRANT option;
flush privileges;
```


### others  
- extract and copy oozie distro.tar to target directory  
- modify hadoop core-site.xml : 

```xml
<!-- conf/hadoop-conf/core-site.xml -->
<!-- OOZIE -->
<!-- root -->
<property>
    <name>hadoop.proxyuser.root.hosts</name>
    <value>*</value>
</property>
<property>
    <name>hadoop.proxyuser.root.groups</name>
    <value>*</value>
</property>
```
- make oozie/libext  
- copy hadoop share/hadoop to libext   
- download ext-2.2.jar to libext. in libext wget http://archive.cloudera.com/gplextras/misc/ext-2.2.zip

- distro 를 oozie 설치할 namenode 로 docker cp 로 복사하고 압축 해제  
- namenode 에서 실행  
- ./oozie-setup.sh prepare-war  
```bash
./bin/oozie-setup.sh sharelib create -fs hdfs://namenode:9000
```
- modify oozie/conf  
```xml 
<!-- oozie/conf/oozie-site.xml -->
<configuration>
    <property>
        <name>oozie.db.schema.name</name>
        <value>oozie</value>
        <description>Oozie DB</description>
    </property>
    <property>
        <name>oozie.service.JPAService.create.db.schema</name>
        <value>true</value>
        <description>Oozie DB</description>
    </property>
    <property>
        <name>oozie.service.JPAService.validate.db.connection</name>
        <value>false</value>
        <description>JDBC Driver class</description>
    </property>
    <property>
        <name>oozie.service.JPAService.jdbc.driver</name>
        <value>com.mysql.jdbc.Driver</value>
        <description>JDBC Driver class</description>
    </property>
    <property>
        <name>oozie.service.JPAService.jdbc.url</name>
        <value>jdbc:mysql://rdb/oozie?useSSL=false</value>
        <description>JDBC URL</description>
    </property>
    <property>
        <name>oozie.service.JPAService.jdbc.username</name>
        <value>oozie_u</value>
        <description>DB user name</description>
    </property>
    <property>
        <name>oozie.service.JPAService.jdbc.password</name>
        <value>oozie_pwd</value>
        <description>DB user password</description>
    </property>
</configuration>
```
```bash
# namenode 
# # cp /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
# cp /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/share/lib/distcp/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
# cp /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/share/lib/git/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
# cp /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/share/lib/hcatalog/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
# cp /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/share/lib/hive/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
# cp /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/share/lib/hive2/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
# cp /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/share/lib/mapreduce-streaming/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
# cp /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/share/lib/oozie/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
# cp /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/share/lib/pig/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
# cp /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/share/lib/spark/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
# cp /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/share/lib/sqoop/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/


cp /hadoop/share/hadoop/client/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
cp /hadoop/share/hadoop/common/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
cp /hadoop/share/hadoop/hdfs/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
cp /hadoop/share/hadoop/mapreduce/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
cp /hadoop/share/hadoop/tools/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/
cp /hadoop/share/hadoop/yarn/*.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/

apt-get install libmysql-java
cp /usr/share/java/mysql.jar /oozie/distro/target/oozie-5.2.0-distro/oozie-5.2.0/libext/

./bin/oozie-start.sh  
```

- distro 를 oozie 설치할 namenode 로 docker cp 로 복사하고 압축 해제  

- oozie-start.sh  
- oozie admin -oozie http://spark-master:11000/oozie-status  
- http://spark-master:11000/oozie/   




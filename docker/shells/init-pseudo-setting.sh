# init-pseudo-setting.sh
# Pseudo-Distributed mode 
# hadoop/core-site.xml, hadoop/hdfs-site.xml setting
HADOOP_HOME=/hadoop/hadoop-3.2.2
cat <<EOF|tee $HADOOP_HOME/etc/hadoop/core-site.xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
EOF

cat <<EOF|tee $HADOOP_HOME/etc/hadoop/hdfs-site.xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
</configuration>>
EOF

echo "[core-site, hdfs-site] setting for Pseudo-Distributed mode completed"
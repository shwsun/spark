# pyspark, jupyter, jdk install
#sudo -i
apt-get update
apt-get install -y python3-pip iputils-ping openjdk-8-jdk 
ln /usr/bin/pip3 /usr/bin/pip
ln /usr/bin/python3 /usr/bin/python
pip install pyspark 
pip install jupyterlab 
echo 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/\nexport SPARK_HOME=/usr/local/lib/python3.6/dist-packages/pyspark\nexport PATH=$PATH:/usr/lib/jvm/java-8-openjdk-amd64/bin/\n' >> ~/.bashrc
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
export SPARK_HOME=/usr/local/lib/python3.6/dist-packages/pyspark
export PATH=$PATH:/usr/lib/jvm/java-8-openjdk-amd64/bin/

# pyspark, jupyter, jdk install
#sudo -i
apt-get update
apt-get install -y python3-pip iputils-ping openjdk-8-jdk 
ln /usr/bin/pip3 /usr/bin/pip
pip install pyspark jupyterlab
echo 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/\nexport PATH=$PATH:/usr/lib/jvm/java-8-openjdk-amd64/bin/\n' >> ~/.bashrc
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
export PATH=$PATH:/usr/lib/jvm/java-8-openjdk-amd64/bin/

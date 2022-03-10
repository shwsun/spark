apt-get update
apt-get install -y python3-pip iputils-ping
ln /usr/bin/pip3 /usr/bin/pip  
pip install jupyterlab
pip install pyspark==3.2.1
pip install findspark
mkdir -p /notebooks
echo "==== jupyter lab, pyspark installed. ===="

# # start jupyter 
# jupyter lab --allow-root --ip='*' --notebook-dir='/notebooks' --workspace='/notebooks' > /dev/null 2>&1 &
# jupyter server list 
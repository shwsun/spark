FROM ubuntu:18.04  

# /home 디렉토리
USER root
RUN mkdir -p /notebooks
# RUN apt-get update
# RUN apt-get install -y python3-pip iputils-ping openjdk-8-jdk 
# RUN ln /usr/bin/pip3 /usr/bin/pip
# RUN pip install pyspark jupyterlab
ADD install-pyspark.sh .
RUN chmod 755 install-pyspark.sh;./install-pyspark.sh 
# --NotebookApp.token='' --NotebookApp.password=''

RUN jupyter lab --allow-root --ip='*'  --notebook-dir='/notebooks' --workspace='/notebooks' > /dev/null 2>&1 & 
CMD /bin/bash
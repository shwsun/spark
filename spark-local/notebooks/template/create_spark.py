# import libraries 
import socket
import sys
import os
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SparkSession
from os.path import abspath
import findspark
import time 

# 전역변수 설정 
# local mode 
SPARK_LOCAL_MASTER = "local[3]"
# client mode 
SPARK_CLUSTER_MASTER = "yarn" #"spark://35.202.237.174:7077" 
SPARK_APP_NAME = "DATA-Preparation"
HOST_NAME = "spark-master" #socket.gethostname()


# Define path
DATA_ROOT = f'{os.getcwd()}/data'
DATA_PATH = f'{DATA_ROOT}'

findspark.init()
print(os.getenv('SPARK_HOME'))

warehouse_location = abspath('/user/hive/warehouse')

# Spark session 생성 메서드 
def init_remote_session(enable_hive=False):
    #SPARK_CLUSTER_MASTER = "spark://34.64.108.172:7077" 
    if enable_hive:
        spark = SparkSession.builder.master(SPARK_CLUSTER_MASTER).appName(SPARK_APP_NAME).config("spark.sql.warehouse.dir", warehouse_location).enableHiveSupport().getOrCreate()
    else :
        spark = SparkSession.builder.master(SPARK_CLUSTER_MASTER).appName(SPARK_APP_NAME).getOrCreate()
    
    return spark
    
# local mode 실행 시 메모리를 확장해야 하는 경우 있어서, conf에 memory 변경 추가  
def init_local_session():
    #SPARK_LOCAL_MASTER = "local[3]"
    spark = SparkSession.builder.master(SPARK_LOCAL_MASTER).appName(SPARK_APP_NAME).config('spark.driver.host', HOST_NAME).getOrCreate()
    default_conf = spark.sparkContext._conf#.getAll()
    print(f'Old Conf : {default_conf.getAll()}')
    conf = spark.sparkContext._conf.setAll([
        ('spark.executor.instances', 1)
        #, ('spark.driver.memory', '12g'), ('spark.executor.memory', '8g'), ('spark.driver.maxResultSize', '8g')
        , ('spark.driver.allowMultipleContexts', 'true'), ('spark.sql.shuffle.partitions', 8)
        ##,('spark.memory.offHeap.enabled', True), ('spark.memory.offHeap.size', '8g')
    ])
    spark.sparkContext.stop()
    
    spark = SparkSession.builder.master(SPARK_LOCAL_MASTER).appName(SPARK_APP_NAME).config(conf=default_conf).getOrCreate()
    new_conf = spark.sparkContext._conf
    print(f'Updated Conf : {new_conf.getAll()}')
    return spark

# 필요 라이브러리 임포트  
import socket
import sys
import os
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SparkSession
from os.path import abspath
import time 

# 스파크 세션을 생성해서 반환  
def spark_creation(app_name):
    spark = SparkSession.builder.master('yarn').appName(app_name)\
    .config('spark.rpc.message.maxSize', '1024')\
    .config('spark.hadoop.dfs.replication', '1')\
    .config('spark.driver.cores', '1').config('spark.driver.memory', '7g')\
    .config('spark.num.executors', '3')\
    .config('spark.executor.cores', '1').config('spark.executor.memory', '7g').getOrCreate()
    # sc = spark.sparkContext
    # sc
    return spark

# 인벤토리 차감 현황 정보 생성  
def create_sample_inventory_ckpt(spark, row_count = 1000*10000, tbl_name="inven/tbl_sample_inventory", partition_num=20, file_format="parquet", write_mode="overwrite"):
    # 샘플 데이터 생성 및 확인 
    sample_data = _create_sample_setops(row_count)
    sample_schema = _define_sample_setops_schema()
    rdd = spark.sparkContext.parallelize(sample_data, partition_num)
    df = spark.createDataFrame(rdd, sample_schema)
    df.write.save(path=tbl_name, format=file_format, mode=write_mode)
    return df  

# 인벤토리 차감 현황 샘플 정보 반환  
def read_sample_inventory_ckpt(spark, tbl_name="inven/tbl_sample_inventory", file_format="parquet"):
    sdf = spark.read.format(file_format).load(tbl_name)
    return sdf



######################## private methods 


# 샘플 데이터 생성 
def _create_sample_setops(row_count = 1000*10000):
    setop_count = row_count
    inv_rate = 100/setop_count
    # 1개월에 최대 1000 건 청약 가정. 
    inv_val = 1000
    inv_req = 0
    setop_name = ['ST_A', 'ST_B', 'ST_C', 'ST_D', 'ST_E', 'ST_F', 'ST_G', 'ST_H', 'ST_I', 'ST_J']
    setops = []
    for s in setop_name:
        for i in range(0, int(setop_count/len(setop_name))):
            setop_id = f'{s}_{i:07d}'
            setops.append([setop_id, s, inv_rate,inv_val,inv_req, inv_rate,inv_val,inv_req\
                           , inv_rate,inv_val,inv_req, inv_rate,inv_val,inv_req, inv_rate,inv_val,inv_req, inv_rate,inv_val,inv_req])
            
    print(setops[-2:])
    return setops
# 샘플 데이터 형식 정의. 읽기/쓰기 편의 제공. 
def _define_sample_setops_schema():
    from pyspark.sql.types import StructType, StructField, StringType, LongType, FloatType
    columns = [
        StructField("setop", StringType())
        , StructField("stype", StringType())
        , StructField("inv_rate_01", FloatType())
        , StructField("inv_val_01", LongType())
        , StructField("inv_req_01", LongType())
        , StructField("inv_rate_02", FloatType())
        , StructField("inv_val_02", LongType())
        , StructField("inv_req_02", LongType())
        , StructField("inv_rate_03", FloatType())
        , StructField("inv_val_03", LongType())
        , StructField("inv_req_03", LongType())
        , StructField("inv_rate_04", FloatType())
        , StructField("inv_val_04", LongType())
        , StructField("inv_req_04", LongType())
        , StructField("inv_rate_05", FloatType())
        , StructField("inv_val_05", LongType())
        , StructField("inv_req_05", LongType())        
        , StructField("inv_rate_06", FloatType())
        , StructField("inv_val_06", LongType())
        , StructField("inv_req_06", LongType())        
    ]
    sample_schema = StructType(columns)
    return sample_schema

# 샘플 타겟 정보 생성. 20 개 카테고리. 
def _create_sample_target():
    segs = []
    seg_count = 20
    for i in range(0, seg_count):
        seg_id = f'CATEGORY_{i:03d}'
        segs.append(seg_id)
            
    print(segs[-2:])
    return segs
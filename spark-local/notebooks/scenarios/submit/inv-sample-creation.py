# 인벤토리 샘플 데이터를 생성  
import socket
import sys
import os
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SparkSession
from os.path import abspath
import findspark
import time 

from pyspark.sql import SparkSession


if __name__ == "__main__":
    """
        Usage: spark-submit --master "yarn" inv-sample-creation.py  
    """
    
    # 환경변수 정의  
    scale = 10 # 1000 만 건 수준
    partition_num = 50
    tbl_setop_name = f'inven/table-set-6m-{partition_num}-{scale}'
    file_format = 'parquet'

    PRJ_ROOT = '/user/shwsun'
    APP_NAME = f'spark-01-sample-creation-6m-{partition_num}-{scale}'
    DB_NAME = 'inven'
    

    # 샘플 데이터 생성 
    def create_setops():
        setop_count = scale * 10000
        inv_rate = 100/setop_count
        # 1개월에 최대 1000 건 청약 가정. 
        inv_val = 1000
        inv_req = 0
        setop_name = ['ST_A', 'ST_B', 'ST_C', 'ST_D', 'ST_E', 'ST_F', 'ST_G', 'ST_H', 'ST_I', 'ST_J']
        setops = []
        for s in setop_name:
            for i in range(0, int(setop_count/len(setop_name))):
                setop_id = f'{s}_{i:07d}'
                setops.append([setop_id, inv_rate,inv_val,inv_req, inv_rate,inv_val,inv_req\
                               , inv_rate,inv_val,inv_req, inv_rate,inv_val,inv_req, inv_rate,inv_val,inv_req, inv_rate,inv_val,inv_req])

        print(setops[-2:])
        return setops
    # 샘플 데이터 형식 정의. 읽기/쓰기 편의 제공. 
    def define_schema():
        from pyspark.sql.types import StructType, StructField, StringType, LongType, FloatType
        columns = [
            StructField("setop", StringType())
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
    def create_target():
        segs = []
        seg_count = 20
        for i in range(0, seg_count):
            seg_id = f'CATEGORY_{i:03d}'
            segs.append(seg_id)

        print(segs[-2:])
        return segs

    
################################################
    spark = SparkSession\
        .builder\
        .appName(APP_NAME)\
        .getOrCreate()

    # 샘플 데이터 생성 및 확인 
    sample_data = create_setops()
    sample_schema = define_schema()

    rdd = spark.sparkContext.parallelize(sample_data, partition_num)
    df = spark.createDataFrame(rdd, sample_schema)

    write_mode = 'overwrite'
    # HDFS 에 /user/root/inven/setop 폴더와 파일이 생성 됨.  
    # 클러스터 메모리/cpu 여유 있으면, 적당한 크기로 한방에 처리.
    df.write.save(path=tbl_setop_name, format=file_format, mode=write_mode)

    # 기록한 파일 다시 읽어 들이기 
    # 저장 결과 확인하기 
    lines = spark.read.format(file_format).option('path', tbl_setop_name).load()
    data_count = lines.count()
    print(f'DATA Count : {data_count:,}')
    lines.show(5)

    spark.stop()

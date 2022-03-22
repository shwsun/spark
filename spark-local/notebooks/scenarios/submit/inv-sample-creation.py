# 인벤토리 샘플 데이터 중 세탑별 할당량 샘플 데이터 생성   
import socket
import sys
import os
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType, FloatType

if __name__ == "__main__":
    """
        Usage: spark-submit --master "yarn" inv-sample-creation.py  
    """
    
    # 환경변수 정의  
    PRJ_ROOT = '/user/shwsun'
    APP_NAME = 'SETOP-SAMPLE-CREATION'
    DB_NAME = 'inventory'
    scale = 10 # 1000 만 건 수준
    partition_num = 5
    tbl_name = 'inventory/inv-setop-sample'
    file_format = 'parquet'
################## 함수 정의 ###################
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
                setop_id = '{}_{:07d}'.format(s, i)
                setops.append([setop_id, inv_rate,inv_val,inv_req, inv_rate,inv_val,inv_req\
                            , inv_rate,inv_val,inv_req, inv_rate,inv_val,inv_req, inv_rate,inv_val,inv_req, inv_rate,inv_val,inv_req])
                
        print(setops[-2:])
        return setops
    # 샘플 데이터 형식 정의. 읽기/쓰기 편의 제공. 
    def define_schema():
        columns = [
            StructField("setop", StringType())
            , StructField("inv_rate_01", FloatType()), StructField("inv_val_01", LongType()), StructField("inv_req_01", LongType())
            , StructField("inv_rate_02", FloatType()), StructField("inv_val_02", LongType()), StructField("inv_req_02", LongType())
            , StructField("inv_rate_03", FloatType()), StructField("inv_val_03", LongType()), StructField("inv_req_03", LongType())
            , StructField("inv_rate_04", FloatType()), StructField("inv_val_04", LongType()), StructField("inv_req_04", LongType())
            , StructField("inv_rate_05", FloatType()), StructField("inv_val_05", LongType()), StructField("inv_req_05", LongType())        
            , StructField("inv_rate_06", FloatType()), StructField("inv_val_06", LongType()), StructField("inv_req_06", LongType())        
        ]
        sample_schema = StructType(columns)
        return sample_schema
    
################################################
    print("================== spark app started ==================")
    spark = SparkSession\
        .builder\
        .appName(APP_NAME)\
        .getOrCreate()
    print("================== spark session created ==================")
    # 샘플 데이터 생성 및 확인 
    sample_data = create_setops()
    sample_schema = define_schema()
    rdd = spark.sparkContext.parallelize(sample_data, partition_num)
    df = spark.createDataFrame(rdd, sample_schema)
    print("================== sample data created ==================")
    print(df)
    print(f"================== data {df.count()} ==================")
    # # HDFS 에 /user/root/inven/setop 폴더와 파일이 생성 됨.  
    # # 클러스터 메모리/cpu 여유 있으면, 적당한 크기로 한방에 처리.
    df.write.save(path=tbl_name, format=file_format, mode="overwrite")
    print("================== overwrite. ==================")
    # #df.show(10)
    # # 기록한 파일 다시 읽어 들이기 
    # # 저장 결과 확인하기 
    lines = spark.read.format(file_format).option('path', tbl_name).load()
    data_count = lines.count()
    lines.show(5)
    # spark 종료
    spark.stop()
    print("================== SPARK STOPPED. ==================")

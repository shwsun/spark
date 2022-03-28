# 인벤토리 샘플 세톱 데이터 1천만 건 6개월 데이터를 읽어서 간단한 차감 실행  
# 총 리소스 4core 16GB를 2 datanode 2 hdd로 나눈 환경에서 150 초 (리포트 생성, rdb write 제외)  
# 
#
# 처리하는 연산은 대략 아래와 같음
# 1. 세톱 인벤 할당 정보 1천만 건 적재 
# 2. 인벤 할당 정보 총량 계산 -> 차감 요청 총량 처리 가능한 지 확인 위해 
# 3. 인벤정보의 비율과 차감 요청을 서로 곱해서 전체 세톱별 차감량 계산 
# 4. 차감할 여유 수량이 존재하는(>0) 인벤 데이터만 필터 
# 5. 첫번째 총량 계산시 처리하지 못하고 남은 수량 차감  
# 6. 차감하고 남은 할당량을 반영해서 인벤정보 새로 기록  
# (7. 차감 세톱 결과 이용해서 리포트 생성)
# (8. 리포트 정보를 rdb에 기록) 
import socket
import sys
import os
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SparkSession
from os.path import abspath
import findspark
import time 
from pyspark.sql.functions import explode, split
from pyspark.sql import SparkSession


if __name__ == "__main__":
    """
        Usage: spark-submit --master "yarn" inv-sample-read.py  
    """
    
    # 환경변수 정의  
    scale = 1000 # 1000 만 건 수준
    partition_num = 50
    tbl_name = 'inven/table-set-6m-20-1000'
    tbl_req = "inven/request"
    file_format = 'parquet'

    PRJ_ROOT = '/user/root'
    APP_NAME = 'spark-01-sample-creation-6m-50-1000'
    DB_NAME = 'inven'

    
################################################
    spark = SparkSession\
        .builder\
        .appName(APP_NAME)\
        .getOrCreate()

    ## 인벤 기준 정보 조회  
    spark.read.format(file_format).load(tbl_name).createOrReplaceTempView('setop_view')
    spark.catalog.cacheTable("setop_view")
    spark.catalog.isCached('setop_view')

    # 1) 총량 계산 : 최초 24 초. 재실행 시 1초 미만. 
    sql_total = "select sum(inv_val_01), sum(inv_val_02), sum(inv_val_03), sum(inv_val_04), sum(inv_val_05), sum(inv_val_06) from setop_view"
    spark.sql(sql_total).show()

    # # 2) 부족 여부 판단. 생략 ... 

    # Stream 요청 처리  

    temp = ['']
    columns = [
        StructField("type", StringType())
        , StructField("qty", LongType())
    ]
    dataSchema = StructType(columns) 
    #lines = spark.readStream.format("hdfs").option("", "").load()
    lines = spark.readStream.schema(dataSchema).csv(f"{PRJ_ROOT}/{tbl_req}")
    
    
    spark.stop()

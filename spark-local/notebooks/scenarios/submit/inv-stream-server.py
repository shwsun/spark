# Stream server를 실행  
# request를 받아서 해당 내용을 request-output 테이블에 기록  
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
from pyspark.sql.types import StructType, StructField, StringType, LongType


if __name__ == "__main__":
    """
        Usage: spark-submit --master "yarn" inv-stream-server.py  
    """
 
    scale = 1000 
    partition_num = 50
    tbl_name = 'inven/table-set-6m-20-1000'
    tbl_req = "inven/request"
    file_format = 'parquet'

    PRJ_ROOT = '/user/root'
    APP_NAME = 'spark-stream-server'
    DB_NAME = 'inven'

    spark = SparkSession\
        .builder\
        .appName(APP_NAME)\
        .getOrCreate()
    print("================== session created. ==================")
    temp = ['']
    columns = [
        StructField("type", StringType())
        , StructField("qty", LongType())
    ]
    dataSchema = StructType(columns) 
    input_table = str.format("{}/{}", PRJ_ROOT, tbl_req)
    lines = spark.readStream.schema(dataSchema).csv(input_table)
    print("================== read stream. ==================")
    query_name = "request-output"
    outQ = lines.writeStream.queryName(query_name).format("console").trigger(processingTime="30 seconds").outputMode("append").start()

    outQ.awaitTermination()
    spark.stop()

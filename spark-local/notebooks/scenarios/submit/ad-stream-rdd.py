# 광고차감 요청을 받아서 처리하는 stream server (rdd 방식) 
# rdd 에서 직접 차감하는 방식을 테스트 해 본다.  
# sql union으로 해결 시, 일부만 차감해도 되는 경우에도, 전체를 대상으로 연산해서 느려서  
# sql union은 항상 일정한 시간.  
# # 차감 대상 조회 + 차감 연산에 걸린 시간 비교 
# 3 node gcp 32 GB  : 40 초   
# 2 node azure 16GB : 90 초   
# 3 node ncloud 32 GB : 70 초  
# 추가 계산해야 할 시간 : 
# 1. APP 생성 : 20 초 
# 2. 캐시 갱신 : 30 초  
# 3. snapshot 저장 : 50 ~ 90 초  
# 4. report 생성 : ?? 미진행 
# 5. rdb insert 50 rows : 5 초  
import socket
import sys
import os
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SparkSession
from os.path import abspath
import time 
from pyspark.sql.functions import explode, split
from pyspark.sql.types import StructType, StructField, StringType, LongType


if __name__ == "__main__":
    """
        Usage: spark-submit --master "yarn" --jars /install-files/mysql-connector-java-5.1.49/mysql-connector-java-5.1.49-bin.jar inv-stream-rdd.py  
    """
 
    scale = 1000 
    partition_num = 50
    shuffle_partitions = 20 
    tbl_name = 'inven/table-set-6m-20-1000'
    tbl_req = "inven/request"
    file_format = 'parquet'

    PRJ_ROOT = '/user/root'
    APP_NAME = 'spark-stream-server'
    DB_NAME = 'inven'

    spark = SparkSession\
        .builder\
        .appName(APP_NAME)\
        .config("spark.sql.shuffle.partitions", shuffle_partitions)\
        .getOrCreate()
    print("================== session created. ==================")
    print("================== Load cache ==================")
    spark.read.format(file_format).load(tbl_name).createOrReplaceTempView('setop_view')
    spark.catalog.cacheTable("setop_view")
    spark.catalog.isCached('setop_view')
    spark.sql("select count(1) from setop_view").show()
    print("================== Caching completed. ==================")

    temp = ['']
    columns = [
        StructField("id", StringType())
        , StructField("qty", LongType())
    ]
    dataSchema = StructType(columns) 
    input_table = str.format("{}/{}", PRJ_ROOT, tbl_req)
    lines = spark.readStream.schema(dataSchema).csv(input_table)
    print("================== read stream. ==================")
    lines.createOrReplaceTempView("lines")
    stream = spark.sql("select id, qty+11 as qty from lines ")
    
    # tmp = spark.sql("select type from lines ")
    # tmp.writeStream.queryName("console-1").format("console").trigger(processingTime="5 seconds").outputMode("append").start()
    
    # jdbc input  
    props = {"driver":"com.mysql.jdbc.Driver"}
    db_url = "jdbc:mysql://rdb/test_jdbc?user=jdbc&password=jdbc"
    tbl = "from_spark"
    #stream = filtered.write.jdbc(db_url, tbl, mode='append', properties=props)
    sql_subtract = """
    select setop, sum(inv_val_01) inv_val_01 
    from 
    (
        select setop, inv_val_01 from setop_view 
        UNION ALL 
        select setop, -qty inv_val_01 from setop_minus 
    ) 
    group by setop 
    """
    def foreach_batch_function(df, epoch_id):
        print(str.format("=============>  DF : {} , id : {}", df, epoch_id))
        df.show()
        rows = df.take(1)
        row = rows[0].asDict()
        id = row["id"]
        qty = row["qty"]
        # inv_val_01
        spark.sql(str.format("select * from setop_view where setop like '{}' limit 10", id)).show()
        
        # 간단 차감 지정한 세탑 종류에서 남은 inv_val_01 의 n % 가져와서 총량에서 차감하기  
        sql_subtract_amount = "select setop, inv_val_01 *({}/100.0) qty from setop_view where setop like '{}'"
        spark.sql(str.format(sql_subtract_amount, qty, id)).createOrReplaceTempView("setop_minus")
        
        spark.sql(sql_subtract).summary().show()
        
        #df.write.jdbc(db_url, tbl, mode='append', properties=props)
        print("=============>  <=============")
    
    query_name = "request-output"
    outQ = stream.writeStream.queryName(query_name).foreachBatch(foreach_batch_function).trigger(processingTime="10 seconds").outputMode("append").start()
    #outQ = stream.writeStream.queryName(query_name).format("console").trigger(processingTime="10 seconds").outputMode("append").start()
    print("================== > stream server started. < ==================")
    outQ.awaitTermination()
    spark.stop()

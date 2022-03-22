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
import time 

from pyspark.sql import SparkSession


if __name__ == "__main__":
    """
        Usage: spark-submit --master "yarn" inv-sample-calc.py  
    """
    
    # 환경변수 정의  
    scale = 1000 # 1000 만 건 수준
    partition_num = 50
    tbl_name = 'inventory/inv-setop-sample'
    file_format = 'parquet'

    PRJ_ROOT = '/user/shwsun'
    APP_NAME = f'spark-inv-sample-calc'
    #DB_NAME = 'inven'
    
################################################
    print("================== spark app started ==================")
    spark = SparkSession\
        .builder\
        .appName(APP_NAME)\
        .getOrCreate()
    print("================== spark session created ==================")

    ## 인벤 기준 정보 조회  
    spark.read.format(file_format).load(tbl_name).createOrReplaceTempView('setop_view')
    spark.catalog.cacheTable("setop_view")
    spark.catalog.isCached('setop_view')

    # 1) 총량 계산 : 최초 24 초. 재실행 시 1초 미만. 
    sql_total = "select sum(inv_val_01), sum(inv_val_02), sum(inv_val_03), sum(inv_val_04), sum(inv_val_05), sum(inv_val_06) from setop_view"
    spark.sql(sql_total).show()
    print("================== setop_view showed ==================")

    # # 2) 부족 여부 판단. 생략 ... 

    # 3) 비율 계산 반올림  
    pcnt = 1000*1000*10 # 100 이어야 하지만 1천만건 하드 코딩 비율 조정 위해 임시값. 
    sql_total = f"select setop, -(inv_val_01*inv_rate_01/{pcnt}) inv_val_01, -(inv_val_02*inv_rate_02/{pcnt}) inv_val_02, -(inv_val_03*inv_rate_03/{pcnt}) inv_val_03\
    , -(inv_val_04*inv_rate_04/{pcnt}) inv_val_04, -(inv_val_05*inv_rate_05/{pcnt}) inv_val_05, -(inv_val_06*inv_rate_06/{pcnt}) inv_val_06 from setop_view"
    sql_all = f"select sum(inv_val_01) inv_val_01, sum(inv_val_02) inv_val_02, sum(inv_val_03) inv_val_03\
    , sum(inv_val_04) inv_val_04, sum(inv_val_05) inv_val_05, sum(inv_val_06) inv_val_06 from ({sql_total}) as AL"

    spark.sql(sql_all).show()
    print("================== AL showed ==================")

    # 3) 차감 계산  
    sql_calc = f"select setop, sum(inv_val_01) inv_val_01 , sum(inv_val_02) inv_val_02, sum(inv_val_03) inv_val_03\
    , sum(inv_val_04) inv_val_04 , sum(inv_val_05) inv_val_05, sum(inv_val_06) inv_val_06 \
    from ( \
    {sql_total} \
    UNION ALL \
    select setop, inv_val_01, inv_val_02, inv_val_03, inv_val_04, inv_val_05, inv_val_06 from setop_view \
    ) as AL \
    group by setop"
    #spark.sql(sql_calc).count()
    spark.sql(sql_calc).createOrReplaceTempView("tbl_subtracted")
    # 차감 스냅샷 기록  
    # ...  

    # 4) 총량 0이 아닌 세톱 조회  
    spark.sql("select * from tbl_subtracted where inv_val_01>0 or inv_val_02>0 or \
    inv_val_03>0 or inv_val_04>0 or inv_val_05>0 or inv_val_06>0 ").createOrReplaceTempView("tbl_remains")

    # 5) 남은 비율 계산 : 42 초    
    # 5-1) (-) 수량. 일단 하드 코딩 
    #spark.sql("select 1000 inv_val_01, 900 inv_val_02, 950 inv_val_03, 850 inv_val_04, 810 inv_val_05, 890 inv_val_06").createOrReplaceTempView("remains_qty")
    remains = [1000, 900, 950, 850, 880, 890]
    totals = """select 
    sum(inv_val_01) inv_val_01, sum(inv_val_02) inv_val_02, sum(inv_val_03) inv_val_03
    , sum(inv_val_04) inv_val_04, sum(inv_val_05) inv_val_05, sum(inv_val_06) inv_val_06 
    from tbl_remains
    """
    spark.sql(totals).createOrReplaceTempView("totals")
    # 5-2) 도수 / 남은 총량. 남은 수량을 차감할 비율. 
    sql_minus_remains = f"""
    select setop
    , -{remains[0]}*tbl_remains.inv_val_01/totals.inv_val_01 inv_val_01, -{remains[1]}*tbl_remains.inv_val_02/totals.inv_val_02 inv_val_02 
    , -{remains[2]}*tbl_remains.inv_val_03/totals.inv_val_03 inv_val_03, -{remains[3]}*tbl_remains.inv_val_04/totals.inv_val_04 inv_val_04 
    , -{remains[4]}*tbl_remains.inv_val_05/totals.inv_val_05 inv_val_05, -{remains[5]}*tbl_remains.inv_val_06/totals.inv_val_06 inv_val_06 
    from tbl_remains cross join totals 
    """
    spark.sql(sql_minus_remains).createOrReplaceTempView("minus_remains")

    # 6) 추가 차감 및 결과 스냅샷 기록 : 70 초   
    sql_result = """
    select setop
    , sum(inv_val_01) inv_val_01 , sum(inv_val_02) inv_val_02
    , sum(inv_val_03) inv_val_03 , sum(inv_val_04) inv_val_04
    , sum(inv_val_05) inv_val_05 , sum(inv_val_06) inv_val_06
    from 
    (
    select * 
    from tbl_subtracted 
    UNION ALL 
    select * 
    from minus_remains
    ) as A 
    group by setop 
    """
    result = spark.sql(sql_result)
    result.write.save(path="result", format=file_format, mode='overwrite')
    print("================== save completed ==================")

    cnt = spark.read.format(file_format).load('result').count()
    print(f'Row count = {cnt:,}')

    # # rdb 쓰기 테스트 
    # props = {"driver":"com.mysql.jdbc.Driver"}
    # db_url = "jdbc:mysql://rdb/test_jdbc?user=jdbc&password=jdbc"
    # tbl = "from_spark"
    # rdb = spark.sql('select * from result limit 10')
    # rdb.write.jdbc(db_url, tbl, mode='overwrite', properties=props)

    spark.stop()

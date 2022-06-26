# 필요 라이브러리 임포트  
import socket
import sys
import os
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SparkSession
from os.path import abspath
import time 
import numpy as np
import pandas as pd
import pyarrow as pa 
import pyarrow.parquet as pq  
import itertools
import gc
# from tqdm import tqdm 
import utils
# import inv_util.py
# import utils.inv_large as large

# DEBUG = InvenUtil._show_debug


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

########        ###########
# 소스 데이터, 체크포인트, 리포트 경로 정의  
DATA_DIR = "./hdfs"
RDB_DIR = "./rdb/"
CKPT_DIR = "./ckpt"
# 원본 데이터 파일 
INIT_FILE_SETOP = f'{DATA_DIR}/setop_6month_10million.parquet'
INIT_FILE_CHANNEL = f'{DATA_DIR}/channel_6month.parquet'
INIT_FILE_SETOP_MAP = f'{DATA_DIR}/setop_target_map.parquet'
# INIT_FILE_SETOP_MAP = f'{CKPT_DIR}/big_map.parquet'
# 체크포인트 데이터 파일 
DATA_FILE_SETOP = f'{CKPT_DIR}/setop_6month_10million.parquet'
DATA_FILE_CHANNEL = f'{CKPT_DIR}/channel_6month.parquet'
DATA_FILE_SETOP_MAP = f'{CKPT_DIR}/setop_target_map.parquet'
# 리포트 결과 파일  
REPORT_FILE_SEG = f'{RDB_DIR}/setop_report_seg.parquet'
REPORT_FILE_LOCATION = f'{RDB_DIR}/setop_report_location.parquet'
REPORT_FILE_CHANNEL = f'{RDB_DIR}/channel_report.parquet'
# SEG:setop 대량 메핑  
BIG_SETOP_MAP = f'{CKPT_DIR}/big_map.parquet'


DF_SETOP, DF_CHN, MAP_SETOP_TARGET = None, None, None 

# 테스트 해 볼 샘플 데이터를 생성  
# 채널, 세탑, 주제/세탑 맵 정보 생성  
def create_sample_data(setop_count=10000000, inv_total_amount=[10000000000, 2000000000, 300000000, 4000000000, 500000000, 6000000000], seg_count=50, setop_per_seg=500000):
    # 인벤 총수량 6개월 분 지정  
    sample_data = utils.inv_large.SampleData(inv_total_amount)
    # 세탑, 지역 차감 기준 데이터
    print(f"-------- 세탑/지역/주제 인벤 --------")
    pdf_st = sample_data.load_setop_base(setop_count)
    # 채널, 시간 , 주말 인벤 생성    
    print(f"-------- 채널/시간/주말 인벤 --------")
    pdf_ch = sample_data.load_channel_base()
    # 타겟 세탑 매핑 정보
    print(f"-------- 타겟-세탑 매핑 정보 --------")
    pdf_st_map = sample_data.load_setop_target_map(pdf_st.setop, seg_count, setop_per_seg)
    return pdf_st, pdf_ch, pdf_st_map

# snapshot 폴더에 원본 데이터를 밀어 넣는다.  
def reset_data():
    table = pq.read_table(INIT_FILE_SETOP)
    pq.write_table(table, DATA_FILE_SETOP)
    del table
    table = pq.read_table(INIT_FILE_CHANNEL)
    pq.write_table(table, DATA_FILE_CHANNEL)
    del table
    table = pq.read_table(INIT_FILE_SETOP_MAP)
    pq.write_table(table, DATA_FILE_SETOP_MAP)
    del table
    gc.collect()

# checkpoint로 저장된 데이터를 읽어들인다.  
# 편의상 전역변수 DF_xx 에 저장해 두고 사용한다.  
# 전역변수에 저장한 결과를 반환하기도 한다.  
def load_data():
    # global DF_SETOP, DF_CHN, MAP_SETOP_TARGET
    paf = pq.read_table(DATA_FILE_SETOP)
    DF_SETOP = paf.to_pandas()
    paf2 = pq.read_table(DATA_FILE_CHANNEL)
    DF_CHN = paf2.to_pandas()
    paf3 = pq.read_table(DATA_FILE_SETOP_MAP)
    MAP_SETOP_TARGET = paf3.to_pandas()
    del paf, paf2, paf3
    return DF_CHN, DF_SETOP, MAP_SETOP_TARGET
    
# 처리한 데이터를 checkpoint로 저장한다.  
def save_data(pdf_setop, pdf_chn):
    table = pa.Table.from_pandas(pdf_setop)
    pq.write_table(table, DATA_FILE_SETOP)
    table = pa.Table.from_pandas(pdf_chn)
    pq.write_table(table, DATA_FILE_CHANNEL)
    
# 처리 결과를 리포트로 가공한다.  
def save_report(report_target, report_location, report_chn):
    report_ready = (report_target is not None) & (report_location is not None) & (report_chn is not None)
    if report_ready:
        table = pa.Table.from_pandas(report_target)
        pq.write_table(table, REPORT_FILE_SEG)
        table = pa.Table.from_pandas(report_location)
        pq.write_table(table, REPORT_FILE_LOCATION)
        table = pa.Table.from_pandas(report_chn)
        pq.write_table(table, REPORT_FILE_CHANNEL)
        return True
    else:
        print("[Error] report data not provided.")
        return False

# report 를 생성하고 결과를 파일로 저장한다.  
# 파일 결과를 rdb에 기록한다.  
# 채널 리포트는 스냅샷을 거의 그대로 
# 세탑은 -> 지역별, SEG 별로 나눠서 기록 
# 모두 처리 index 컬럼 추가  
def report(df_subtract, df_ch_subtract):
    report_target, report_location, report_chn = None
    report_chn = df_ch_subtract
    # seg가 setop과 1:1 이 아니라 groupby로 요약되지 않는다.  
    # seg 별로 해당 조건 조회해서 요약해야 한다.  
    # 주제 200 개면, 200 번 
    # report_target = ....... 
    # 지역별 요약 
    report_location = df_subtract.groupby("location")
    
    save_report(report_target, report_location, report_chn)

# 샘플 데이터를 생성해서 초기 데이터 폴더에 배치한다.  
def initialize_sample_data(setop_count=10000000, inv_total_amount=[10000000000, 20000000000, 30000000000, 40000000000, 50000000000, 60000000000]):
    # 6개월 인벤토리 총량  
    # inv_total_amount=[10000000000, 20000000000, 30000000000, 40000000000, 50000000000, 60000000000]
    DF_SETOP, DF_CHN, MAP_SETOP = create_sample_data(setop_count, inv_total_amount)
    print(f"세탑 : {DF_SETOP.shape}, 채널 {DF_CHN.shape}, 주제맵 {MAP_SETOP.shape}")
    table = pa.Table.from_pandas(DF_SETOP)
    pq.write_table(table, DATA_FILE_SETOP)
    del table, DF_SETOP
    table = pa.Table.from_pandas(DF_CHN)
    pq.write_table(table, DATA_FILE_CHANNEL)
    del table, DF_CHN
    table = pa.Table.from_pandas(MAP_SETOP)
    pq.write_table(table, DATA_FILE_SETOP_MAP)
    del table, MAP_SETOP
    print(f"{DATA_FILE_CHANNEL}, {DATA_FILE_SETOP}, {DATA_FILE_SETOP_MAP} data file created.")
    
###############################################
class InvenUtil:
    
    """
    인벤토리에서 수량을 차감하는 로직  
    """
    def __init__(self):
        self._verbose = False
        # self._inv_total_amount = inv_total_amount

    def __str__(self):
        return f'str : {self._data_count}'

    def __repr__(self):
        return f'repr : {self._data_count}'
    # 비율 적용한 수량(소수점 포함)과 최초 요청 수량(정수)을 입력받아서, 정수 수준으로 분배한 값을 반환
    # 소수점 이하 자리 비율대로 최초 요청에서 정수로 분배되지 않고 남은 수량을 재분배한다.  
    # pcnt_rate : 원본 비율 목록 % , amount_total : 총량  
    # 입력되는 rated_amounts 가 round가 아닌, floor 값이어야 한다.  
    # Largest Remainder Method algorithm 참고.  
    @classmethod
    def redistribute_int(cls, floored_amounts, amount_total):
        import math
        import numpy as np 
        # 소수점을 처리 : 나머지 총량을 기여율 순으로 1 로 할당  
        # 요청 총량과 내림 총량 차이 만큼을 잔여 비율 높은 순으로 재할당 (1씩)  
        # 나머지 모두 0 처리 
        amount_fractioned = floored_amounts.copy() #.reset_index(drop=True)
        floored =  np.floor(amount_fractioned)#fractioned_tmp.apply(math.floor)#.reset_index(drop=True)
        # 나머지 큰 순서로 n 개 위치
        InvenUtil._show_debug(f"[redistribute_int] amount_total : {amount_total} , floored sum : {np.sum(floored)}")
        n = int(amount_total - np.sum(floored))
        w_idx = list(np.argsort(-(amount_fractioned % 1))[:n])
        # 큰거 n 개만 +1 처리  
        InvenUtil._show_debug(f"[redistribute_int] w_idx = {len(w_idx)}, {w_idx}")
        InvenUtil._show_debug(f"[redistribute_int] before = {amount_fractioned}")
        InvenUtil._show_debug(f"[redistribute_int] floored  = {floored}")
        floored[w_idx] = floored[w_idx] + 1    # 내림값 중 상위 n개(w_idx)에 자투리 대신 1을 추가  
        redistribute_values = floored.astype(np.int64)
        InvenUtil._show_debug(f"[redistribute_int] after  = {redistribute_values}")
        return redistribute_values

    _verbose = False
    """
    상세 디버그 기능 설정
    """
    @classmethod
    def verbose(cls, verb):
        cls._verbose = verb
      
    """
    상세 디버그 로그를 화면에 출력  
    """
    @classmethod
    def _show_debug(cls, msg):
        if cls._verbose:
            print(msg)
        else:
            pass
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
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
import itertools
import gc
import utils
import utils.inv_util as inv
import pyarrow as pa 
# from tqdm import tqdm

DEBUG = utils.inv_util.InvenUtil._show_debug

class SampleData:
    """
    인벤토리 샘플 데이터를 생성
    """
    def __init__(self, inv_total_amount=[100000000, 2000000000, 300000000, 4000000000, 520000000, 6000000000]):
        self._inv_total_amount = inv_total_amount
        precision_scale = np.int64(1000000000)
        self.set_precision_scale(precision_scale)


    def __str__(self):
        return f'str : {self._data_count}'

    def __repr__(self):
        return f'repr : {self._data_count}'
    # float 나누기나 비율 연산시 안전하게 처리할 수 있는 자릿수의 역수.
    # 너무 큰 값을 지정하면, overflow가 발생해서 (-) 값으로 계산될 수 있다. 
    # 이 값은 나눗셈 연산 시, 임시로 몫을 크게해서 소수점 이하 자릿수를 많이 살리는 용도로 승수로 사용한다.  
    def set_precision_scale(self, precision_scale):
        self._precision_scale = precision_scale
    def get_precision_scale(self):
        return self._precision_scale
   
    
    # 채널, 시간대, 주중/주말 인벤토리 기준값 샘플 데이터 생성  
    def load_channel_base(self):
        arr_chn = ['CH-a', 'CH-b', 'CH-c']
        arr_time = list(range(0, 23))
        arr_week = ['week', 'weekend']

        list_all = list(itertools.product(arr_chn, arr_time, arr_week))
        row_count = len(list_all)

        totals = self._inv_total_amount #[100000000, 2000000000, 300000000, 4000000000, 520000000, 6000000000] #self._inv_total_amount
        int_amount_m = []
        rates_pcnt_m = []
        # 시드 고정, 비율 샘플링.  
        for m in range(0, 6):
            total_amount = totals[m]
            np.random.seed(m+1)
            precision_scale = self.get_precision_scale()
            _ = np.random.choice(range(0, 1000), row_count) 
            rates = _.astype('int64')*precision_scale / _.astype('int64').sum()
            # print(f"rates : {rates}")
            rates = rates/precision_scale
            # total_amount = self._inv_total_amount
            rated_amounts = total_amount*rates.astype('float64')
            print(f"rated_amounts sum : {np.sum(rated_amounts)}")
            rates_pcnt = np.round(rates*100 , 6) 
   
            redistribute_int_amount = inv.InvenUtil.redistribute_int(rated_amounts, total_amount) 
            rates_pcnt_m.append(rates_pcnt)
            int_amount_m.append(redistribute_int_amount)
            print(f"redistribute_int_amount sum : {np.sum(redistribute_int_amount)}")
            
        pdf_chn = pd.DataFrame(list_all, columns=["channel", "hour", "week"])
        for m in range(0, 6):
            pdf_chn[f"req_cum_{m+1:02}"] = 0
            pdf_chn[f"rate_{m+1:02}"] = rates_pcnt_m[m]
            pdf_chn[f"amount_base_{m+1:02}"] = int_amount_m[m]       
            pdf_chn[f"residual_{m+1:02}"] = pdf_chn[f"amount_base_{m+1:02}"]

        del list_all, int_amount_m, rates_pcnt_m
        gc.collect()
        print(f"shape : {pdf_chn.shape}, 비율 <0 : {(pdf_chn.rate_01<0).sum()}, 수량 <0 : {(pdf_chn.amount_base_01<0).sum()}" )

        return pdf_chn


    # 세탑, 지역별 인벤토리 기준값  
    # 세탑, 지역, 비율, 인벤토리값  
    # 만들어야 할 데이터가 커서, arrow 이용해서 만든다.  
    def load_setop_base(self, setop_count=10000000):
        # 세탑 데이터 생성  
        # setop_count = 10000000
        setop_type = ['ST_A', 'ST_B', 'ST_C', 'ST_D', 'ST_E', 'ST_F', 'ST_G', 'ST_H', 'ST_I', 'ST_J']
        location = ['LC_A', 'LC_B', 'LC_C', 'LC_D', 'LC_E', 'LC_F', 'LC_G', 'LC_H', 'LC_I', 'LC_J']
        setops = []
        locations = []
        for s, loc in zip(setop_type, location):
            for i in range(0, int(setop_count/len(setop_type))):
                setop_id = f'{s}_{i:08d}'
                setops.append(setop_id)
                locations.append(loc)

        # 수량 및 비율 정보 생성  
        totals = self._inv_total_amount
        int_amount_m = []
        rates_pcnt_m = []
        decimal_point = 8 
        # 6개월분 할당량 생성  
        for m in range(0, 6):
            total_amount = totals[m]
            np.random.seed(m+1)
            # decimal point 8th precision 
            precision_scale = self.get_precision_scale()
            _ = np.random.choice(range(1, 2000), setop_count) #(np.random.random_sample(setop_count)*value_sacle).astype(int)
            rates = _.astype('int64')*precision_scale / _.astype('int64').sum()
            # print(f"rates : {rates}")
            rates = rates/precision_scale
            # total_amount = self._inv_total_amount
            rated_amounts = total_amount*rates.astype('float64')
            print(f"rated_amounts sum : {np.sum(rated_amounts)}")
            rates_pcnt = np.round(rates*100 , decimal_point) 
            # rates_pcnt[:10]
            redistribute_int_amount = inv.InvenUtil.redistribute_int(rated_amounts, total_amount) 
            rates_pcnt_m.append(rates_pcnt)
            int_amount_m.append(redistribute_int_amount)
            print(f"redistribute_int_amount sum : {np.sum(redistribute_int_amount)}")

        schema = pa.schema({
                "setop"  : pa.string(),
                "location" : pa.string(),
                "rate_01" : pa.float32(), "amount_base_01"  : pa.int64(),
                "req_cum_01" : pa.int64(), "residual_01" : pa.int64(),
                "rate_02" : pa.float32(), "amount_base_02"  : pa.int64(),
                "req_cum_02" : pa.int64(), "residual_02" : pa.int64(),
                "rate_03" : pa.float32(), "amount_base_03"  : pa.int64(),
                "req_cum_03" : pa.int64(), "residual_03" : pa.int64(),
                "rate_04" : pa.float32(), "amount_base_04"  : pa.int64(),
                "req_cum_04" : pa.int64(), "residual_04" : pa.int64(),
                "rate_05" : pa.float32(), "amount_base_05"  : pa.int64(),
                "req_cum_05" : pa.int64(), "residual_05" : pa.int64(),
                "rate_06" : pa.float32(), "amount_base_06"  : pa.int64(),
                "req_cum_06" : pa.int64(), "residual_06" : pa.int64(),
           }) 
        # pdf.head()
        zeros = np.zeros(len(setops))
        paf = pa.Table.from_pydict(
            {"setop"  : setops, "location"  : locations
            , "rate_01"  : rates_pcnt_m[0], "amount_base_01"  : int_amount_m[0]
            , "req_cum_01"  : zeros , "residual_01"  : int_amount_m[0]
            , "rate_02"  : rates_pcnt_m[1], "amount_base_02"  : int_amount_m[1]
            , "req_cum_02"  : zeros , "residual_02"  : int_amount_m[1]
            , "rate_03"  : rates_pcnt_m[2], "amount_base_03"  : int_amount_m[2]
            , "req_cum_03"  : zeros , "residual_03"  : int_amount_m[2]
            , "rate_04"  : rates_pcnt_m[3], "amount_base_04"  : int_amount_m[3]
            , "req_cum_04"  : zeros , "residual_04"  : int_amount_m[3]
            , "rate_05"  : rates_pcnt_m[4], "amount_base_05"  : int_amount_m[4]
            , "req_cum_05"  : zeros , "residual_05"  : int_amount_m[4]
            , "rate_06"  : rates_pcnt_m[5], "amount_base_06"  : int_amount_m[5]
            , "req_cum_06"  : zeros , "residual_06"  : int_amount_m[5]}    
            , schema
        )
        
        pdf = paf.to_pandas()
        print(f"shape : {pdf.shape}, 비율 <0 : {(pdf.rate_01<0).sum()}, 수량 <0 : {(pdf.amount_base_01<0).sum()}" )
        # del columns_setop, _, rates, rated_amounts, rates_pcnt, setop_type, location, setops, locations, redistribute_int_amount
        del paf
        gc.collect()
        return pdf

    # setop_map 을 반환  
    def load_setop_target_map(self, sr_setop, seg_count=50, setop_per_seg=500000):
        return self.seg_map_from_setop(sr_setop, seg_count, setop_per_seg)
        
    # setop_map 을 반환  
    # 일부 setop이 겹치도록, category A,B 2개 타겟으로 데이터 생성  
    def seg_map_hardcoding(self):
        # 세탑 카테고리 맵  
        setop_map = {"target":["A", "A", "A", "A", "B", "B", "B", "C"],  "setop":["ST_A_00000000", "ST_B_00000000", "ST_C_00000000", "ST_D_00000000", "ST_C_00000000", "ST_D_00000000", "ST_E_00000000", "ST_C_00000000"]}
        pdf = pd.DataFrame(setop_map, columns=["target", "setop"])
        return pdf

    def seg_map_from_setop(self, sr_setop, seg_count=50, setop_per_seg=500000):
        targets = []
        setops = []
        target_ids = range(1, seg_count+1)
        id_max = len(sr_setop)
        for t in tqdm(target_ids):
            tmp_tar = np.full((setop_per_seg), t)
            targets.extend(tmp_tar)
            setops.extend( sr_setop.sample(setop_per_seg).values )  
        df_map = pd.DataFrame(columns=["target", "setop"])
        df_map["target"] = targets
        del targets
        df_map["setop"] = setops
        print(f"MAP_SETOP_TARGET : {df_map.shape}")
        del setops 
        return df_map
    
    ######################## private methods 
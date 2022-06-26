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

DEBUG = utils.inv_util.InvenUtil._show_debug

class SampleData:
    """
    인벤토리 샘플 데이터를 생성
    """
    def __init__(self, inv_total_amount=1000):
        self._inv_total_amount = inv_total_amount

    def __str__(self):
        return f'str : {self._data_count}'

    def __repr__(self):
        return f'repr : {self._data_count}'
    
    
    # 채널, 시간대, 주중/주말 인벤토리 기준값 샘플 데이터 생성  
    def load_channel_base(self):
        columns = ["channel", "hour", "week", "req_cum_01", "rate_01", "amount_base_01",  "residual_01"]
        arr_chn = ['CH-a', 'CH-b', 'CH-c']
        arr_time = list(range(0, 23))
        arr_week = ['week', 'weekend']

        total_amount = self._inv_total_amount
        list_all = list(itertools.product(arr_chn, arr_time, arr_week))
        row_count = len(list_all)
        # 시드 고정, 비율 샘플링.  
        np.random.seed(1)
        _ = np.random.choice(range(0, 1000), row_count) 
        rates = np.round(_ / _.astype(np.int64).sum() , 8) 
        total_amount = self._inv_total_amount
        rated_amounts = total_amount*rates.astype(np.float64)
        rates_pcnt = np.round(rates * 100, 6)   
        
        pdf_chn = pd.DataFrame(list_all)
        pdf_chn["req_cum_01"] = 0
        pdf_chn["rate_01"] = rates_pcnt
        redistribute_int_amount = inv.InvenUtil.redistribute_int(rated_amounts, total_amount) 
        pdf_chn["amount_base_01"] = redistribute_int_amount       
        pdf_chn["residual_01"] = pdf_chn["amount_base_01"]
        pdf_chn.columns = columns
        # print(pdf_chn.sum())
        # pdf_chn.tail()
        del columns, list_all, _, rates, rated_amounts, rates_pcnt, redistribute_int_amount
        gc.collect()
        print(f"shape : {pdf_chn.shape}, 비율 <0 : {(pdf_chn.rate_01<0).sum()}, 수량 <0 : {(pdf_chn.amount_base_01<0).sum()}" )
        return pdf_chn


    # 세탑, 지역별 인벤토리 기준값  
    # 세탑, 지역, 비율, 인벤토리값  
    def load_setop_base(self, setop_count=10):
        columns_setop = ["setop", "location", "rate_01", "amount_base_01"]
        # 세탑용 샘플 데이터 : 세탑 보유수량 정보  
        value_sacle = 1#100 # 수량 뻥튀기  
        #rate_scale = 100 # %
        # 시드 고정, 비율 샘플링. 비율합이 100%가 되도록 데이터 랜덤 생성  
        np.random.seed(1)
        _ = np.random.choice(range(0, 1000), setop_count) #(np.random.random_sample(setop_count)*value_sacle).astype(int)
        rates = np.round(_ / _.astype(np.int64).sum() , 8) 
        total_amount = self._inv_total_amount
        rated_amounts = total_amount*rates.astype(np.float64)
        rates_pcnt = np.round(rates * 100, 6) 

        setop_type = ['ST_A', 'ST_B', 'ST_C', 'ST_D', 'ST_E', 'ST_F', 'ST_G', 'ST_H', 'ST_I', 'ST_J']
        location = ['LC_A', 'LC_B', 'LC_C', 'LC_D', 'LC_E', 'LC_F', 'LC_G', 'LC_H', 'LC_I', 'LC_J']
        setops = []
        locations = []
        for s, loc in zip(setop_type, location):
            for i in range(0, int(setop_count/len(setop_type))):
                setop_id = f'{s}_{i:08d}'
                setops.append(setop_id)
                locations.append(loc)
        pdf = pd.DataFrame(columns=["setop", "location", "rate_01", "amount_base_01", "req_cum_01", "residual_01"])
        pdf["setop"] = setops
        pdf["location"] = locations
        pdf["req_cum_01"] = 0
        pdf["rate_01"] = rates_pcnt #np.round(rates_pcnt, 3) 
        
        #         DEBUG(f"mini_setop_base.rates : {rates_pcnt}")
        redistribute_int_amount = inv.InvenUtil.redistribute_int(rated_amounts, total_amount) 
        pdf["amount_base_01"] = redistribute_int_amount
        pdf["residual_01"] = pdf["amount_base_01"]
        # del columns_setop, _, rates, rated_amounts, rates_pcnt, setop_type, location, setops, locations, redistribute_int_amount
        # gc.collect()
        print(f"shape : {pdf.shape}, 비율 <0 : {(pdf.rate_01<0).sum()}, 수량 <0 : {(pdf.amount_base_01<0).sum()}" )
        return pdf
    
    # setop_map 을 반환  
    # 일부 setop이 겹치도록, category A,B 2개 타겟으로 데이터 생성  
    def load_setop_target_map(self):
        # 세탑 카테고리 맵  
        setop_map = {"target":["A", "A", "A", "A", "B", "B", "B", "C"],  "setop":["ST_A_00000000", "ST_B_00000000", "ST_C_00000000", "ST_D_00000000", "ST_C_00000000", "ST_D_00000000", "ST_E_00000000", "ST_C_00000000"]}
        pdf = pd.DataFrame(setop_map, columns=["target", "setop"])
        return pdf
    ######################## private methods 
# 필요 라이브러리 임포트  
import socket
import sys
import os
import gc 
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SparkSession
from os.path import abspath
import time 
import numpy as np
import pandas as pd
import itertools
import math
import utils
import utils.inv_util
from utils.inv_request import InvReq 

DEBUG = utils.inv_util.InvenUtil._show_debug
class InvenSubtract:

    """
    인벤토리에서 수량을 차감하는 로직  
    성능 문제 때문에 차감 처리 시, 입력 데이터 테이블을 직접 변경한다.  
    따라서, 입력 데이터를 보존해야 하는 상황이면, 입력에 복사본을 넘겨야 한다.  
    """
    def __init__(self):
        self._verbose = False
        # self._inv_total_amount = inv_total_amount

    def __str__(self):
        return f'str : {self._data_count}'

    def __repr__(self):
        return f'repr : {self._data_count}'
    
#     """
#     상세 디버그 기능 설정
#     """
#     def verbose(self, verb):
#         self._verbose = verb
        
#     """
#     상세 디버그 로그를 화면에 출력  
#     """
#     def _show_debug(msg):
#         if self._verbose:
#             print(msg)
#         else:
#             pass
        
   
    def _check_amount_available(self, df_subtract, req_amount, month):
        str_month = f"{month:02}"
        col_rate, col_req_cum, col_residual, col_amount_base = f"rate_{str_month}", f"req_cum_{str_month}", f"residual_{str_month}", f"amount_base_{str_month}"
        # print(f"col_residual : {col_residual}")
        # print(f"df_subtract :\n{df_subtract}")
        residual_amount = df_subtract[col_residual].sum()
        is_avail_amount = residual_amount>=req_amount
        # if is_avail_amount : 
        #     print(f"[차감 가능] [{str_month} 월차] : {residual_amount} - {req_amount} = {residual_amount-req_amount}")
        # else:
        #     print(f"[수량 부족] [{str_month} 월차] : {residual_amount} - {req_amount} = {residual_amount-req_amount}")
        return is_avail_amount
       
    # category(setop), location 2개 조건에 대한 where-like 연산 처리  
    # 조건이 둘 모두 지정된 경우에는 모두를 만족하는 결과를 반환.
    def filter_setop_conditions(self, df_org, inv_req:InvReq, setop_map):
        # setops 에 해당하는 inv 만 계산해서 합한다.
        df_filtered = df_org
        df_margin = None
        if not inv_req.is_setop:
            print(f"[WARN] : Inventory request is made for 'channel' but used as 'setop'.")
        is_seg_assigned = (inv_req.categories is not None) and len([inv_req.categories])>0
        if is_seg_assigned:
            setops = setop_map.setop[setop_map.target.isin(inv_req.categories)].values
            df_org.set_index(["setop"], inplace=True, drop=False)
            idx_seg = df_org.index.isin(setops)
        else :
            idx_seg = np.full(len(df_org.index), True)  

        # df_org.set_index(["location"], inplace=True, drop=False)
        is_location_assigned = (inv_req.locations is not None) and len([inv_req.locations])>0
        if is_location_assigned:
            idx_location = df_org.location.isin(inv_req.locations)
        else:
            idx_location = np.full(len(df_org.index), True)  

        idx = idx_seg & idx_location
        # print(f"req : {inv_req} , loc : {len([inv_req.locations])}")
        # print(f"idx : {len(idx)} , idx_seg : {len(idx_seg)}, idx_location : {len(idx_location)}")
        # print(f"idx : {np.sum(idx)} , idx_seg : {np.sum(idx_seg)}, idx_location : {np.sum(idx_location)}")

        df_filtered = df_org[idx]
        df_margin = df_org[~idx]
        del idx, idx_seg, idx_location
        return df_filtered, df_margin


    # 채널/시간대/주중주말 조건을 적용하고, 필터링한 결과와 나머지 데이터를 반환한다.  
    # 필터 결과와 나머지 결과를 같이 반환하는 이유는, 차감 계산이 끝난 후에 다시 원본에 차감한 결과만 갱신된 형태로 원본과 같은 형태의 데이터를 생성해야 하기 때문.  
    def filter_channel_conditions(self, df_org, inv_req:InvReq):
        # setops 에 해당하는 inv 만 계산해서 합한다.
        df_filtered = df_org
        df_margin = None
        # 요청 객체 타입 확인 
        if inv_req.is_setop:
            print(f"[WARN] : Inventory request is made for 'setop' but used as 'channel'.")
        # 채널 조건 필터
        is_channel_assigned = (inv_req.channels is not None) and len([inv_req.channels])>0
        if is_channel_assigned:
            idx_channel = df_org.channel.isin(inv_req.channels)
        else :
            idx_channel = np.full(len(df_org.index), True)  
        # 시간대 조건 필터
        is_time_assigned = (inv_req.times is not None) and len([inv_req.times])>0
        if is_time_assigned:
            idx_time = df_org.hour.isin(inv_req.times)
        else:
            idx_time = np.full(len(df_org.index), True)  
        # 주중주말 조건 필터  
        is_week_type_assigned = (inv_req.week_types is not None) and len([inv_req.week_types])>0
        if is_week_type_assigned:
            idx_week = df_org.week.isin(inv_req.week_types)
        else:
            idx_week = np.full(len(df_org.index), True)  
        # 필터 결과 종합  
        idx = idx_channel & idx_time & idx_week 
        # print(f"req : {inv_req} , loc : {len([inv_req.locations])}")
        # print(f"idx : {len(idx)} , idx_channel : {len(idx_channel)}, idx_time : {len(idx_time)}, idx_week : {len(idx_week)}")
        # print(f"idx : {np.sum(idx)} , idx_channel : {np.sum(idx_channel)}, idx_time : {np.sum(idx_time)}, idx_week : {np.sum(idx_week)}")

        df_filtered = df_org[idx]
        df_margin = df_org[~idx]
        del idx, idx_channel, idx_time, idx_week
        return df_filtered, df_margin

    # 전체 또는 지정한 세탑에 대해 수량 차감  
    # 채널 필터 조건은 : 채널, 시간, 주중주말  
    # 조건 필터가 필요한 경우, 외부에서 미리 처리해서 조건에 해당하는 setop 목록을 넘기거나, 
    # 입력 데이터로 미리 필터링한 데이터를 넘긴다. 이 경우에는 setops 값은 None으로 넘기면 성능 향상이 있다. 
    def _subtract_amount_available(self, df_in, req_amount, month): # , filter_cond=None):
        str_month = f"{month:02}"
        col_rate, col_req_cum, col_residual, col_amount_base = f"rate_{str_month}", f"req_cum_{str_month}", f"residual_{str_month}", f"amount_base_{str_month}"
        # df_filtered = df_in
        availables = np.array(df_in[col_residual].values)
        availables[np.argwhere(availables<0)] = 0
        rate_total = np.sum(availables)
        req_rated_amount = (req_amount * (availables/rate_total))
        # 소수점 이하 자리 재분배  
        redistribute_values = utils.inv_util.InvenUtil.redistribute_int(req_rated_amount, req_amount)
        DEBUG(f"redistribute_values = {redistribute_values}")
        DEBUG(f"df_in : \n{df_in}")
        DEBUG(f"req_cum = {df_in[col_req_cum].values}")
        # 데이터 차감값 누적 기록 
        df_in[col_req_cum] = df_in[col_req_cum] + redistribute_values
        df_in[col_residual] = df_in[col_residual] - redistribute_values #df_filtered.req_cum
        DEBUG(f"df_in : \n{df_in}")
        return df_in

    # 잔여 수량이 부족해서 잔여 비율로 분배할 수 없는 경우에 대한 처리
    # 최초의 차감 비율을 일률적으로 적용해서 (-) 수량이 발생해도 차감을 계속 처리  
    def _subtract_amount_short(self, df_in, req_amount, month): 
        str_month = f"{month:02}"
        col_rate, col_req_cum, col_residual, col_amount_base = f"rate_{str_month}", f"req_cum_{str_month}", f"residual_{str_month}", f"amount_base_{str_month}"
        # 채널 조건일 경우에는 세탑 차감 필터가 아닌 다른 필터가 필요. 아직 처리하지 않음.  
        # df_filtered = df_in
        base_total = df_in[col_amount_base].astype('int64').sum()
        rates = df_in[col_amount_base].astype('int64').values/base_total
        req_rated_amount = (req_amount * rates)
        # 소수점 이하 자리 재분배  
        redistribute_values = utils.inv_util.InvenUtil.redistribute_int(req_rated_amount, req_amount)
        DEBUG(f"redistribute_values = {redistribute_values}")
        DEBUG(f"df_in : \n{df_in}")
        DEBUG(f"req_cum = {df_in[col_req_cum].values}")
        # 데이터 차감값 누적 기록 
        df_in[col_req_cum] = df_in[col_req_cum] + redistribute_values
        df_in[col_residual] = df_in[col_residual] - redistribute_values #df_filtered.req_cum
        DEBUG(f"df_in : \n{df_in}")
        return df_in
 
    # setop, channel input data가 바른지 확인한다.  
    # 입력이 이상하면 처리를 진행하지 않게 한다.  
    def check_valid_input(self, df_st_base, df_ch_base):
        error_message = ""
        is_valid = (df_st_base is not None) and (df_ch_base is not None)
        if is_valid:
            error_message = "residual total is different between setop and channel data."
            is_valid = df_st_base.residual_01.sum()==df_ch_base.residual_01.sum()
        else:
            error_message = "input data is null."
        # if is_valid:
        return is_valid, error_message   
    
    # 충분차감, 부분차감 로직을 상황에 맞게 섞어서 차감 로직을 실행한다.  
    # 남은 수량이 충분한 경우에는 남은 수량 비율로 분배해서 차감 처리한다. 분배 비율은 최초 참고용.  
    # 남은 수량이 부족한 경우에도 수량이 부족하다는 표시만하고, 차감은 계속 실행한다.  
    # -> 이 경우, 남은 수량 비율?이라는 정의가 성립하지 않기 때분에, 최초 차감 비율을 적용해서 차감을 계속 처리한다. (-) 수량이 발생하는 상황.  
    #     
    def subtract_runner(self, df_st_base, df_ch_base, setop_map, filter_conditions:InvReq): 
        # return 
        df_setop_calced, df_ch_calced = None, None
        is_valid_input, error_message = self.check_valid_input(df_st_base, df_ch_base)
        if not is_valid_input:
            print(f"[invalid input] : {error_message}")
            # 차감하지 않은 결과를 반환  
            df_setop_calced, df_ch_calced = df_st_base, df_ch_base
        else : 
            
            # 필터 : 차감은 차감 대상 데이터에 대해서만 처리 
            df_setop_filtered, df_setop_margin = self.filter_setop_conditions(df_st_base, filter_conditions, setop_map)
            df_ch_filtered, df_ch_margin = self.filter_channel_conditions(df_ch_base, filter_conditions) 
            # 필터 결과가 어느 한쪽만 0이면, 한쪽에서만 차감이 실행되서, 양쪽 잔여 수량이 달라지게 된다.  
            # 필터 결과가 어느 한쪽만 0이면, 에러 메시지를 출력하고 차감을 진행하지 않는다.  
            if len(df_ch_filtered)<1 or len(df_setop_filtered)<1:
                print("There is no target to subtract.")
                # 차감하지 않은 결과를 반환  
                df_setop_calced, df_ch_calced = df_st_base, df_ch_base
                return df_setop_calced, df_ch_calced
           
            # df_filtered, df_margin = self._filter_setops(df_st_base, setops)
            df_setop_subtract, df_ch_subtract = df_setop_filtered, df_ch_filtered
            for month_index in range(0, len(filter_conditions.subtract_amounts)):
                # 차감 전 총 수량 확인 
                str_month = f"{(month_index+1):02}"
                col_residual = f"residual_{str_month}"
                print(f"====> {str_month} Before(ST/CH) : {df_setop_subtract[col_residual].sum()} / {df_ch_subtract[col_residual].sum()}")
                df_setop_subtract, df_ch_subtract = self.subtract_month(df_setop_subtract, df_ch_subtract, setop_map, month_index, filter_conditions)
                print(f"====> {str_month} After(ST/CH) : {df_setop_subtract[col_residual].sum()} / {df_ch_subtract[col_residual].sum()}")

            # ......  
#             str_month = f"{month:02}"
#             col_rate, col_req_cum, col_residual, col_amount_base = f"rate_{str_month}", f"req_cum_{str_month}", f"residual_{str_month}", f"amount_base_{str_month}"
#             is_avail_amount = self._check_amount_available(df_setop_filtered, req_amount, month)
            # 필터하지 않은 나머지와 필터하고 계산한 결과 병합 
            # 세탑 데이터 병합 
            df_setop_calced = self.concatenate_filter_margin(df_setop_subtract, df_setop_margin)
            # 채널 데이터 병합
            df_ch_calced = self.concatenate_filter_margin(df_ch_subtract, df_ch_margin)

        return df_setop_calced, df_ch_calced
            
        
    def concatenate_filter_margin(self, df_filtered, df_margin):
        # 데이터 병합
        # if (df_margin is not None) &  (df_filtered is not None):
        # print(f"concat : {df_margin.shape} + {df_filtered.shape}")
        df_calced = pd.concat([df_margin, df_filtered]) 
        # print(f"concat df_ch_calced : {df_ch_calced.shape}")        
        # print(f"after cat : {time.strftime('%X', time.localtime())}")
        # print(f"====> ST : {df_setop_calced.shape}, {req_amount}, {df_setop_calced.residual_01.sum()}")
        # print(f"CALCED : {df_setop_calced.req_cum_01.sum()}, {df_setop_calced.residual_01.sum()} / {df_setop_calced.req_cum_02.sum()}, {df_setop_calced.residual_02.sum()}")
        # print(f"CAL_CH : [{df_ch_calced.shape}] {df_ch_calced.req_cum_01.sum()}, {df_ch_calced.residual_01.sum()} / {df_ch_calced.req_cum_02.sum()}, {df_ch_calced.residual_02.sum()}")
        print(f"concat df_calced : {df_margin.shape} + {df_filtered.shape} = {df_calced.shape}")
        return df_calced
            
            
    # 지정한 월에 대한 인벤토리 차감처리  
    # 대상 수량이 없어서
    def subtract_month(self, df_setop_filtered, df_ch_filtered, setop_map, month_index, filter_conditions:InvReq): 
        month = month_index+1
        str_month = f"{month:02}"
        col_residual = f"residual_{str_month}"
        # 차감 처리  
        # 1. 전체 수량 확인  
        req_amount = filter_conditions.subtract_amounts[month_index] #req_more[0] # 이 값이 이번 차감 요청 수량  
       
        # 차감 진행  
        if req_amount>0:
            is_avail_amount = self._check_amount_available(df_setop_filtered, req_amount, month)
            if is_avail_amount: 
                # print(f"====> 세탑 충분차감 전 - 대상/요청/잔여총량 : {df_setop_filtered.shape} / {req_amount} / {df_setop_filtered[col_residual].sum()}")
                # print(f"====> 채널 충분차감 전 - 대상/요청/잔여총량 : {df_ch_filtered.shape} / {req_amount} / {df_ch_filtered[col_residual].sum()}")
                df_setop_subtract = self._subtract_amount_available(df_setop_filtered, req_amount, month) 
                df_ch_subtract = self._subtract_amount_available(df_ch_filtered, req_amount, month) 
            else :
                print("====> Although not sufficient amount. Continue subtraction.  <====")
                # print(f"====> 세탑 부족차감 전 - 대상/요청/잔여총량: {df_setop_filtered.shape} / {req_amount} / {df_setop_filtered[col_residual].sum()}")
                # print(f"====> 채널 부족차감 전 - 대상/요청/잔여총량: {df_ch_filtered.shape} / {req_amount} / {df_ch_filtered[col_residual].sum()}")
                df_setop_subtract = self._subtract_amount_short(df_setop_filtered, req_amount, month) 
                df_ch_subtract = self._subtract_amount_short(df_ch_filtered, req_amount, month)
        else:
            df_setop_subtract = df_setop_filtered
            df_ch_subtract = df_ch_filtered
            
        del df_setop_filtered, df_ch_filtered
        return df_setop_subtract, df_ch_subtract
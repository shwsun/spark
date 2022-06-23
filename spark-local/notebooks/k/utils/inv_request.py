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
import utils
import utils.inv_util
import math

"""
인벤 차감 요청   
아래와 같은 요청을 처리할 수 있게 요청 값을 저장한다.  
- 전체  
- 채널/시간대  
- 주중주말  
- 채널/시간대/주중주말  
- 세탑 타게팅  
- 지역 타게팅  
- 세탑/지역 타게팅  
"""
class InvReq:
    """
    수량은 0, is_setop은 True, 나머지값은 None 으로 생성  
    None 인 경우, 해당 조건은 아예 적용되지 않는다.  
    []인 경우에는 값이 적용되서, 아무런 값과도 일치하지 않는 조건 비교가 발생해 0 row가 검색된다.  
    months : 1 ~ 6. 최대 6개 지정 가능. 범위를 벗어난 지정은 무시.  
    subtract_amounts : 길이 6인 int 배열. 배열 원소는 각각 1~6월차의 차감 수량을 의미한다.  
      차감을 원하지 않는 월차는 수량 0을 지정해서, 원소의 갯수가 6개가 되도록 한다.  
    """
    def __init__(self, request_index, subtract_amounts=[0,0,0,0,0,0], is_setop=True):
        self.request_index = request_index
        self.subtract_amounts = subtract_amounts
        self.is_setop = is_setop
        self.__channels = None
        self.__times = None
        self.__week_types = None
        self.__categories = None
        self.__locations = None

    def __str__(self):
        # return f'str : {self._subtract_amount}'
        return self.__repr__()

    def __repr__(self):
        return f'request_index : {self.request_index}, is_setop : {self.is_setop}, subtract_amounts : {self.subtract_amounts}, categories:{self.categories}, locations:{self.locations}, channels:{self.channels}, times:{self.times}, week_types:{self.week_types}'

    @property
    def request_index(self):
        return self.__request_index
    @request_index.setter
    def request_index(self, value):
        if not isinstance(value, int): 
            raise TypeError("request_index must be set to an int")
        self.__request_index = value
    @property
    def is_setop(self):
        return self.__is_setop
    @is_setop.setter
    def is_setop(self, value):
        if not isinstance(value, bool): 
            raise TypeError("is_setop must be set to an bool")
        self.__is_setop = value
    @property
    def subtract_amounts(self):
        return self.__subtract_amounts
    """
    subtract_amounts must be set to an int array-like which length is 6. 
    each elements mean n'th month subctract amount.  
    element value 0 means that there is no subtraction for that month.  
    if you input values below zero those will be converted to 0.  
    """
    @subtract_amounts.setter
    def subtract_amounts(self, value):
        if not hasattr(value, "__len__"): 
            raise TypeError("subtract_amounts must be set to an array-like integer.")
        if len(value)!=6:
            raise TypeError("subtract_amounts must be set to length 6 array-like.")
        all_int = all(isinstance(n, int) for n in value)
        if not all_int:
            raise TypeError("subtract_amounts's element must be set to an int.")
        new_value = [max(a,0) for a in value]
        self.__subtract_amounts = new_value
    @property
    def channels(self):
        return self.__channels
    @channels.setter
    def channels(self, value):
        if not hasattr(value, "__len__") or isinstance(value, str): 
            raise TypeError("channels must be set to an string array-like")
        self.__channels = value
    @property
    def times(self):
        return self.__times
    @times.setter
    def times(self, value):
        if not hasattr(value, "__len__") or isinstance(value, str): 
            raise TypeError("times must be set to an string array-like")
        self.__times = value
    @property
    def week_types(self):
        return self.__week_types
    @week_types.setter
    def week_types(self, value):
        if not hasattr(value, "__len__") or isinstance(value, str): 
            raise TypeError("week_types must be set to an string array-like")
        self.__week_types = value
    @property
    def categories(self):
        return self.__categories
    @categories.setter
    def categories(self, value):
        if not hasattr(value, "__len__") or isinstance(value, str): 
            raise TypeError("categories must be set to an string array-like")
        self.__categories = value
    @property
    def locations(self):
        return self.__locations
    @locations.setter
    def locations(self, value):
        if not hasattr(value, "__len__") or isinstance(value, str): 
            raise TypeError("locations must be set to an string array-like")
        self.__locations = value
    # @property
    # def months(self):
    #     return self.__months
    # """
    # months must be set to an int array-like.  
    # values not in 1~6 are ignored. 
    # if there's no valid value then [1] is used.
    # """
    # @months.setter
    # def months(self, value):
    #     if not hasattr(value, "__len__"): 
    #         raise TypeError("months must be set to an int array-like. values not in 1~6 are ignored. if there's no valid value then [1] is used.")
    #     valid_months = np.array([1,2,3,4,5,6])
    #     valid_value = list(valid_months[np.isin(valid_months, value)])
    #     if not valid_value:
    #         valid_value = [1]
    #     self.__months = valid_value
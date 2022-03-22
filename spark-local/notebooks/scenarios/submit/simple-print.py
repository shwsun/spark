from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType, FloatType
import datetime 

if __name__ == "__main__":

    PRJ_ROOT = '/user/shwsun'
    APP_NAME = 'SETOP-SAMPLE-CREATION'
    DB_NAME = 'inventory'
    scale = 600 
    partition_num = 50
    tbl_name = 'inventory/inv-setop-sample'
    file_format = 'parquet'

    def create_setops():
        setop_count = scale * 10000
        inv_rate = 100.0/setop_count
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

    print("================== spark app started ==================")
    print("================== {} ==================".format(datetime.datetime.now()))
    spark = SparkSession.builder.getOrCreate()
    print("================== spark session created ==================")
    print("================== {} ==================".format(datetime.datetime.now()))
    sample_data = create_setops()
    sample_schema = define_schema()
    rdd = spark.sparkContext.parallelize(sample_data, partition_num)
    df = spark.createDataFrame(rdd, sample_schema)
    print("================== {} ==================".format(datetime.datetime.now()))
    print("================== sample data created ==================")
    print(df)
    df.write.save(path=tbl_name, format=file_format, mode="overwrite")
    print("================== {} ==================".format(datetime.datetime.now()))
    print("================== overwrite. ==================")
    lines = spark.read.format(file_format).option('path', tbl_name).load()
    data_count = lines.count()
    lines.show(5)
    print("================== {} ==================".format(datetime.datetime.now()))

    spark.stop()
    print("================== SPARK STOPPED. ==================")
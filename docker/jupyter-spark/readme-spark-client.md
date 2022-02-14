# Spark client mode Jupyter 연결  

```bash
docker run -itd --privileged --name spark-client --hostname spark-client --rm -p 8888:8888 -p 4040-4050:4040-4050 -v /spark-git/spark/spark-local/notebooks:/notebooks shwsun/jupyter-spark:1.2
# token 확인 
docker exec -it spark-client jupyter server list

```

## Spark client Dockerfile 빌드  


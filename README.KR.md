# spark

- Spark, Hadoop, [Hive], python, jupyter lab  
- spark standalone cluster  
  
This project is aim for creating spark exercise environment and making spark getting-started guide which is able to run purely within this project.  

### Pre-requisite

- Ubuntu 18.04 (docker)
- RAM >= 8 GB  


---  
# 테스트용 VM 구성  
Virtualbox(vagrant)나 GCP를 이용해 machine을 준비하는 과정을 설명합니다.  
실행해 볼 수 있는 machine을 이미 준비해 둔 경우에는 이 단계는 생략합니다.  
준비 과정은 각각 [`host-vm`], [`gcp`] 부분에서 자세하게 설명합니다.  
  
  
---  
# 실행 순서  
이 프로젝트는 아래와 같은 순서로 진행합니다.  
1. 실행 환경(machine) 준비  
 - 로컬 VM 환경  
 - GCP 환경  
 - code-server 
2. Spark local mode 최소(pyspark + Jupyter) 실행  
3. pyspark 최소 설치로 원격 spark cluster 사용하기  
4. Spark local mode + Hdfs + Hive 실행  
5. Spark Cluster mode 간단 설치(Docker-compose. bitnami container image)  
6. Spark cluster에 kafka 추가  
7. Spark cluster에 Ignite 추가  
8. Spark Cluster + Hdfs + Hive 직접 구성  
9. Oozie 추가  
10. Zeppelin 추가  
  
---  
# GCP spark-env 실행하기  
1. spark-env start 
2. ssh spark-env 
3. code-server start 
```bash
code-server --bind-addr 0.0.0.0:80 > /dev/null 2>&1 &  
cat ~/.config/code-server/config.yaml 
# 연결 후 /spark-git/spark로 오픈 폴더 변경  
```
4. spark-client jupyter run   
```bash
docker run -itd --privileged --name spark-client --hostname spark-client --rm -p 8888:8888 -p 4040-4050:4040-4050 -v /spark-git/spark/spark-local/notebooks:/notebooks shwsun/jupyter-spark:1.2
# token 확인 
docker exec -it spark-client jupyter server list
```
5. hdfs-single run   
```bash
docker run -itd --privileged --name hdfs-single --hostname hdfs-single --rm shwsun/hdfs-single
```

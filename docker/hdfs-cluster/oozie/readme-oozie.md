# Oozie install  

- https://dlcdn.apache.org/oozie/5.2.1/oozie-5.2.1.tar.gz  
- tar 압축 해제  
- pom 파일 수정. 클라우데라 url 제거. hadoop 등 버전 변경  
- bin/mkdistro.sh -DskipTests  
- https://oozie.apache.org/docs/5.2.1/ENG_Building.html  

### in spark-master  
docker exec -it spark-master /bin/bash  
```bash
apt-get install -y maven  

```

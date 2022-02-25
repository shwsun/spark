# Hive + metastore  
```bash
docker build -t meta-tmp . 
docker run -it --name meta meta-tmp /bin/bash
```

schematool -dbType mysql -info 
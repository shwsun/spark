# namenode의 ssh key를 datanode로 복사  
# 모든 서버의 ~/.ssh/id_rsa 파일의 내용을 합쳐서 각각의 서버의 ~/.ssh/authorized_keys 파일에 추가
echo "==> Copy ssh key into workers."
docker cp namenode:/root/.ssh/id_rsa.pub ./tmp-share/key_pub
cat ./tmp-share/key_pub > ./tmp-share/id_rsa.pub
docker cp datanode:/root/.ssh/id_rsa.pub ./tmp-share/key_pub
cat ./tmp-share/key_pub >> ./tmp-share/id_rsa.pub
chmod 0600 ./tmp-share/id_rsa.pub

docker cp ./tmp-share/id_rsa.pub namenode:/root/.ssh/authorized_keys 
docker cp ./tmp-share/id_rsa.pub datanode:/root/.ssh/authorized_keys
echo "==> Start ssh daemon in workers."
docker exec -u root -it namenode /etc/init.d/ssh stop
docker exec -u root -it namenode /etc/init.d/ssh start
docker exec -u root -it datanode /etc/init.d/ssh stop
docker exec -u root -it datanode /etc/init.d/ssh start
# namenode의 ssh key를 datanode로 복사  
# 모든 서버의 ~/.ssh/id_rsa 파일의 내용을 합쳐서 각각의 서버의 ~/.ssh/authorized_keys 파일에 추가
echo "==> Clear old data directory."
docker exec -u root -it namenode rm -f /root/.ssh/known_hosts
echo "==> Copy ssh key into workers."
docker cp namenode:/root/.ssh/id_rsa.pub ./tmp-share/key_pub
cat ./tmp-share/key_pub > ./tmp-share/id_rsa.pub
docker cp dn01:/root/.ssh/id_rsa.pub ./tmp-share/key_pub
cat ./tmp-share/key_pub >> ./tmp-share/id_rsa.pub
docker cp dn02:/root/.ssh/id_rsa.pub ./tmp-share/key_pub
cat ./tmp-share/key_pub >> ./tmp-share/id_rsa.pub
docker cp dn03:/root/.ssh/id_rsa.pub ./tmp-share/key_pub
cat ./tmp-share/key_pub >> ./tmp-share/id_rsa.pub

docker cp ./tmp-share/id_rsa.pub namenode:/root/.ssh/authorized_keys 
docker cp ./tmp-share/id_rsa.pub dn01:/root/.ssh/authorized_keys
docker cp ./tmp-share/id_rsa.pub dn02:/root/.ssh/authorized_keys
docker cp ./tmp-share/id_rsa.pub dn03:/root/.ssh/authorized_keys
docker exec -u root -it namenode chmod 0600 /root/.ssh/authorized_keys 
docker exec -u root -it dn01 chmod 0600 /root/.ssh/authorized_keys
docker exec -u root -it dn02 chmod 0600 /root/.ssh/authorized_keys
docker exec -u root -it dn03 chmod 0600 /root/.ssh/authorized_keys
echo "==> Start ssh daemon in workers."
docker exec -u root -it namenode /etc/init.d/ssh stop;
docker exec -u root -it namenode /etc/init.d/ssh start;
docker exec -u root -it dn01 /etc/init.d/ssh stop;
docker exec -u root -it dn01 /etc/init.d/ssh start;
docker exec -u root -it dn02 /etc/init.d/ssh stop;
docker exec -u root -it dn02 /etc/init.d/ssh start;
docker exec -u root -it dn03 /etc/init.d/ssh stop;
docker exec -u root -it dn03 /etc/init.d/ssh start;
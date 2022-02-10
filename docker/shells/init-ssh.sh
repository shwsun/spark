#! init-ssh.sh  
# password 없이 ssh 연결하도록 연결키 설정하고, ssh 서비스 실행해 둔다.  
# 프람프트 없이 자동 실행되도록 처리
echo -e 'y\n' | ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys

#sudo /etc/init.d/ssh start
/etc/init.d/ssh start
ssh -o StrictHostKeyChecking=no localhost
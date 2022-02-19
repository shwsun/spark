# 소스 코드 편집 환경 설정  
파이썬, 자바, 스칼라 개발 환경 설정을 위해 IDE로는 `Jupyter Lab`, `Web Code-server(VisualStudio Code Web)`를 사용합니다.  
해당 IDE를 설치하고 환경 설정하는 방법을 설명합니다.  

서버에 web으로 연결해서 개발해야 하는 상황을 가정해 설명합니다. 
로컬에 직접 GUI 를 지원하는 IDE를 설치할 수 있는 경우에는 직접 IDE를 설치해서 사용하는 것이 더 편합니다. 
직접 GUI 환경 IDE를 설치하는 경우는 따로 설명하지 않습니다.  

`Code-server`를 구성하는 경우에는 git 연동하는 부분까지 설명합니다. 
실제 이 프로젝트를 `Code-server`, `VisualStudio Code`를 `git` 연동해서 Web과 Desktop 환경을 오가며 작성하고 있습니다.  
  
> `VisualStudio Code`의 경우, 로컬에 GUI IDE를 설치하고 ssh 연결을 이용해 원격 서버에 연결하는 개발환경을 쉽게 구축할 수 있습니다.  
> 서버에 ssh 연결이 가능한 상황이면, 굳이 `Web Code-Server`를 설치하지 않고, `VisualStudio Code`를 원격 연결하기만 하면 됩니다.  
> 아주 먼 훗날에, 이에 대한 설명을 추가할 수도 있습니다.  
> 설명할 게 많아서, 언제 추가하게 될 지는 모릅니다.    
  
## Code-Server 직접 실행 
```bash
code-server --bind-addr 0.0.0.0:80 > /dev/null 2>&1 &  
cat ~/.config/code-server/config.yaml  
```

  
---  
## Code-Server container 실행  
개발할 소스 프로젝트를 컨테이너와 볼륨 공유 설정하고, 코드 서버 컨테이너를 실행한다.  
  
code-server 에 대한 설명은 아래 git을 참고합니다.  
[https://github.com/coder/code-server](https://github.com/coder/code-server)  
  
- code server 작업 경로 생성  
```bash
# connect to VM using SSH  
# in SSH you can do 'paste'(Ctrl+v) with (Ctrl + Shift + v)
# in VM run below 
sudo -i 
mkdir /spark-git
cd /spark-git  
# git clone https://github.com/shwsun/spark.git
# check git pulled
cd /spark-git/spark 
ls -l 
```

- code server 실행하기  
IDE 에서 작업 경로로 사용할 소스 경로를 container volume으로 mount 해서 실행한다.  
콘솔창이 code server 실행으로 인해 점유되면 불편하기에 백그라운드에서 실행한다.  
```bash
# connect to VM using SSH  
sudo -i 
cd /spark-git/spark 
# run background mode 
docker run -p 9999:8080 \
  -v "$PWD:/home/coder/project" \
  -u "$(id -u):$(id -g)" \
  -e "DOCKER_USER=$USER" \
  -e "PASSWORD=my_password" \
  -itd bencdr/code-server-deploy-container:latest > /dev/null 2>&1 & 

# http://<your ip>:9999
# type 'my_password' in password prompt then you can loging code-server web  
```
  
실행 후에는 웹 브라우저를 이용해 아래와 같이 코드 서버에 연결할 수 있습니다.  
[Code Server login](!imgs/codeserver-login.png)  
[Code Server welcome](!imgs/codeserver-welcome.png)  

---  
# code-server install 
vm 에 직접 설치  
```bash
# as user account
sudo -i
curl -fsSL https://code-server.dev/install.sh | sh
code-server --bind-addr 0.0.0.0:80 > /dev/null 2>&1 &  
cat ~/.config/code-server/config.yaml  
```

code-server bare metal 에 연결하고 인증(config.yaml 의 키를 입력)하면, web code-server를 사용할 수 있습니다.  
code-server의 폴더 경로를 `Open Folder` 메뉴를 이용해 <스파크 프로젝트 소스 경로>('/spark-git/spark')로 변경합니다.  
코드서버의 View>Terminal 메뉴를 이용해 터미널을 열고, 기본 git 설정을 진행합니다.  
```bash
# code server git 연결 초기 설정  
git config --global user.name "shwsun"
git config --global user.email "shwsun@naver.com"  
git remote add origin https://github.com/shwsun/spark.git
# git hub token 방식 연결 설정. ......  
git credential-cache exit
git config credential.helper cache
git push https://github.com/shwsun/spark.git

```
  
spark scala 개발 환경을 설정하기 위해 extension으로 scala metal 을 설치.  
jupyter는 code web에서 화면이 보이지 않아서, code 로 실행하지 않고 따로 실행.  
scala, java : code-server  
python : jupyter  
 

---  
### code-server service 등록  
```bash
#code-server --bind-addr 0.0.0.0:80 > /dev/null 2>&1 &  
vi /etc/systemd/system/code-server.service

# <service name>.service
[Unit]
Description=Code-Server Service
[Service]
User=root
WorkingDirectory=/spark-git/spark
ExecStart=/usr/bin/code-server \
  --bind-addr 0.0.0.0:80
Restart=always
[Install]
WantedBy=multi-user.target

# Register the Service
systemctl daemon-reload
systemctl enable code-server@"--bind-addr 0.0.0.0:80" 
systemctl start code-server
systemctl status code-server
```

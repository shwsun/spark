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
1. 개발환경 준비 : code-server  
2. hdfs + hive + spark cluster 준비   
3. spark 개발환경으로 hue 연동   
4. spark 개발환경으로 jupyter lab 연동  

  
---  
# Code-Server 설치하기  
개발환경 자체를 `code-server`를 이용해 편집하기 위해 host machine에 직접 설치합니다.   
GCP 에서 VM 을 생성해 사용하는 경우, GCP SSH 콘솔에서 아래와 같이 실행합니다.  
```bash
sudo -i
curl -fsSL https://code-server.dev/install.sh | sh
```
코드서버가 정상 작동하는 지 실행하기 위해 실행해 봅니다.  
```bash
code-server > /dev/null 2>&1 &
# 아래와 같이 코드 서버 설정을 확인할 수 있습니다. 
cat ~/.config/code-server/config.yaml
```
지정한 포트로 실행하고 외부 접속을 허용하기 위해 아래와 같이 설정을 변경하고 서비스로 등록합니다.   
코드서버 포트가 GCP 방화벽에 열려 있어야 합니다.  
```bash
sudo -i
vi ~/.config/code-server/config.yaml
# 
bind-addr: 0.0.0.0:8888
auth: password
password: <password_you_want>
cert: false
# 기존 코드 서버 실행 프로세스 죽이기
kill -9 ...
# 서비스 등록 
systemctl enable --now code-server@$USER
```

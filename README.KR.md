# spark

- Spark, Hadoop, [Hive], python, jupyter lab  
- spark standalone cluster  
  
This project is aim for creating spark exercise environment and making spark getting-started guide which is able to run purely within this project.  

### Pre-requisite

- Ubuntu 18.04 (docker)


---  
# 테스트용 VM 구성  
exercise 환경을 구성할 ubuntu 머신이 없는 경우, 아래와 같이 ubuntu vm을 생성해 사용(Windows OS 사용자)  
vagrant + virtualbox + ubuntu  
- VirtualBox-6.1.30-148432-Win.exe [](https://download.virtualbox.org/virtualbox/6.1.30/VirtualBox-6.1.30-148432-Win.exe) 
- vagrant_2.2.19_x86_64.msi [vagrant 2.2.19 다운로드 경로](https://www.vagrantup.com/downloads) 
- Oracle_VM_VirtualBox_Extension_Pack-6.1.30.vbox-extpack [](https://download.virtualbox.org/virtualbox/6.1.30/Oracle_VM_VirtualBox_Extension_Pack-6.1.30.vbox-extpack) 
- bionic-server-cloudimg-amd64-vagrant.box [Ubuntu:bionic 다운로드 경로](https://app.vagrantup.com/ubuntu/boxes/bionic64)  
  
1. virtualbox 설치  
2. virtualbox extension 설치(생략 가능)  
2. vagrant 설치(설치 후 재시작 필요)  
3. ubuntu box 등록  

위 3번에서 다운받은 ubuntu:bionic image를 vagrant cache에 추가  
베이그런트에 한번 등록해 두면 내부 캐쉬에 저장되서 이후에는 이름으로 바로 호출 가능.
매 번 다운로드 받아서 등록해 줄 필요 없음.  
단, 베이그런트 완전 삭제시에는 캐쉬가 사라지므로 이미지 파일을 다시 등록해야 사용 가능.  
ubuntu box를 다운받은 경로로 이동해서 아래와 같은 명령으로 ubuntu virtualbox image 등록  
vagrant box add ubuntu bionic-server-cloudimg-amd64-vagrant.box
  

git config --global user.name "shwsun"
git config --global user.email "shwsun@naver.com"
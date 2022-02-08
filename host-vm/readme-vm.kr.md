# 테스트용 VM 구성  
exercise 환경을 구성할 ubuntu 머신이 없는 경우, 아래와 같이 ubuntu vm을 생성해 사용(Windows OS 사용자)  
vagrant + virtualbox + ubuntu  
- VirtualBox-6.1.30-148432-Win.exe [](https://download.virtualbox.org/virtualbox/6.1.30/VirtualBox-6.1.30-148432-Win.exe) 
- vagrant_2.2.19_x86_64.msi [vagrant 2.2.19 다운로드 경로](https://www.vagrantup.com/downloads) 
- Oracle_VM_VirtualBox_Extension_Pack-6.1.30.vbox-extpack [](https://download.virtualbox.org/virtualbox/6.1.30/Oracle_VM_VirtualBox_Extension_Pack-6.1.30.vbox-extpack) 
- bionic-server-cloudimg-amd64-vagrant.box [Ubuntu:bionic 다운로드 경로](https://app.vagrantup.com/ubuntu/boxes/bionic64)  
  
1. virtualbox 설치  
2. virtualbox extension 설치(생략 가능)  
3. vagrant 설치(설치 후 재시작 필요)  
4. ubuntu virtualbox 용 image를 vagrant cache에 등록  

다운받은 ubuntu:bionic image를 vagrant cache에 추가  
베이그런트에 한번 등록해 두면 내부 캐쉬에 저장되서 이후에는 이름으로 바로 호출 가능.
매 번 다운로드 받아서 등록해 줄 필요 없음.  
단, 베이그런트 완전 삭제시에는 캐쉬가 사라지므로 이미지 파일을 다시 등록해야 사용 가능.  
ubuntu box를 다운받은 경로로 이동해서 아래와 같은 명령으로 ubuntu virtualbox image 등록  
```bash
# run below command in which .box file is located 
vagrant box add ubuntu bionic-server-cloudimg-amd64-vagrant.box
``` 
### create ubuntu vm setting file(Vagrantfile)
```ruby
Vagrant.configure("2") do |config|
    # config.vbguest.auto_update = false
    # test linux 
    config.vm.define "test" do |vname|
        vname.vm.box = "ubuntu"
        vname.vm.hostname = "test"
        vname.trigger.before :halt do |trigger|
            trigger.warn = "graceful shutdown hook"
            trigger.run_remote = {inline: "echo 'test machine now shutting down'"}
        end
        vname.vm.provider "virtualbox" do |vb|
            vb.name = "test"
            vb.customize ['modifyvm', :id, '--audio', 'none']
            vb.memory = 2000
            vb.cpus = 2
        end
        vname.vm.network "private_network", ip: "192.168.56.10"
    end
end  
```  
  
---  
### ubuntu vm booting  
```bash
# assume that 'Vagrantfile' already prepared
# change directory to vagrant root in which folder 'Vagrantfile' exist. (./spark/host-vm)  
# cd <vagrant root>
vagrant up test
```
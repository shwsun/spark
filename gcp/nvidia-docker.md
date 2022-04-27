```bash
lshw -C display  

add-apt-repository ppa:graphics-drivers/ppa
apt update
apt install -y ubuntu-drivers-common 
ubuntu-drivers autoinstall
ubuntu-drivers devices  
# nvidia-driver-470  
#add-apt-repository ppa:graphics-drivers/ppa
apt-cache search nvidia | grep nvidia-driver-470
apt-get install nvidia-driver-470

apt-get install -y build-essential git python3-dev python3-pip libopenexr-dev libxi-dev \
                     libglfw3-dev libglew-dev libomp-dev libxinerama-dev libxcursor-dev
#dpkg -i cuda-repo-ubuntu1804-10-1-local-10.1.105-418.39_1.0-1_amd64.deb  

curl https://get.docker.com | sh && sudo systemctl --now enable docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
      && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
      && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
apt-get update
apt-get install -y nvidia-docker2  
systemctl restart docker
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
docker run --gpus all -it --rm -p 80:8888 nvcr.io/nvidia/tensorflow:22.03-tf1-py3

# in docker (jupyter terminal)
apt purge cmake 
wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | apt-key add -
apt-get update
apt-get install -y software-properties-common
apt-add-repository 'deb https://apt.kitware.com/ubuntu/ bionic main'
apt-get update
apt-get install -y cmake
# apt-get install -y libxss-dev libxxf86vm-dev libxkbfile-dev libxv-dev
# apt-get install -y libxrandr-dev 
apt-get install -y build-essential git python3-dev python3-pip libopenexr-dev libxi-dev libglfw3-dev libglew-dev libomp-dev libxinerama-dev libxcursor-dev
```  

git clone --recursive https://github.com/nvlabs/instant-ngp
import os 
os.chdir("./instant-ngp")
os.getcwd()
!cmake . -B build
!cmake --build build --config RelWithDebInfo -j 16
./build/testbed --scene data/nerf/fox


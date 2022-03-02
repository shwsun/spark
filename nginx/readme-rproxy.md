vi /etc/nginx/sites-available/code.conf
ln -s /etc/nginx/sites-available/code.conf /etc/nginx/sites-enabled/code.conf  
  
vi /etc/nginx/sites-available/namenode.conf

```bash
# cd nginx 
cp default.conf /etc/nginx/sites-available/default.conf
ln -s /etc/nginx/sites-available/default.conf /etc/nginx/sites-enabled/default.conf  
#기존 conf 제거 
rm /etc/nginx/sites-enabled/code.conf 
nginx -s reload
```


systemctl daemon-reload
systemctl restart nginx



클러스터 내부 서비스 프락시 사용하기  
아래와 같이 클러스터 내부 ip를 vm host 내부에 등록  
```bash
vi /etc/hosts
172.21.0.2 namenode
172.21.0.3 dn01
172.21.0.4 dn02
172.21.0.5 dn03
172.21.0.6 hue
```


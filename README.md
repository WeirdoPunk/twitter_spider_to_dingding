# twitter_spider_to_dingding

爬取指定推特用户最新推文推送到钉钉

#填写 twitter_spiter.py 里的 webhook 和 secret

#在 coin_ur.ini 里添加需要爬取的用户推特主页地址

#安装chrome
sudo touch /etc/default/google-chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

#安装过程如果有依赖错误执行
sudo apt-get -f install

#查看chrome版本
dpkg -l | grep chrome

#安装对应版本driver
在http://chromedriver.storage.googleapis.com/index.html  复制对应版本链接
wget http://chromedriver.storage.googleapis.com/89.0.4389.23/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
chmod +x chromedriver
sudo mv chromedriver /usr/bin

#装crawlertool包
pip3 install crawlertool

#装selenium包
pip3 install selenium

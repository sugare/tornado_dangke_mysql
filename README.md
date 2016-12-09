python 2.7.12<br/>
tornado 4.4.2<br/>
mysql 5.6<br/>

pip install tornado<br/>
pip install torndb<br/>
pip install xlrd<br/>
pip install xlwt<br/>
pip install futures<br/>
sudo apt-get install python-mysqldb supervisor nginx<br/>

#
# 创建库
CREATE DATABASE dang DEFAULT CHARACTER SET utf8;

#
# 给予权限
GRANT ALL PRIVILEGES ON dang.* TO 'dang'@'localhost' IDENTIFIED BY 'dang';

#
# 进入schema.sql所在目录， 创建表
mysql --user=dang --password=dang --database=dang < schema.sql

#
# 上传题库和用户
python updata.py

#
# 运行程序
python manage.py

#
# 开始考试
http://IP/

#
# 查看成绩
http://IP/score


#
# 加入nginx和supervisor
1. 复制conf/nginx.conf到/etc/nginx/nginx.conf
``` Ubuntu 16.04
sudo cp conf/nginx.conf /etc/nginx/
```
2. 复制conf/tornado.conf /etc/supervisor/conf.d/
```
sudp cp conf/tornado.conf /etc/supervisor/conf.d/
```
3. 检查supervisor是否成功运行
```
   sudo supervisorctl
```
4. 给予/var/www目录权限
```
chown -R www-data /var/www 
```
5. 检查nginx是否成功运行
```
http://IP
```

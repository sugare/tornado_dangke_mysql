python 2.7.12<br/>
tornado 4.4.2<br/>
mysql 5.6<br/>
```
sudo pip install tornado
sudo pip install torndb
sudo pip install xlrd
sudo pip install xlwt
sudo pip install futures
sudo apt-get install python-mysqldb supervisor nginx
```

#
# 创建库
```
CREATE DATABASE dang DEFAULT CHARACTER SET utf8;
```
#
# 给予权限
GRANT ALL PRIVILEGES ON dang.* TO 'dang'@'localhost' IDENTIFIED BY 'dang';

#
# 进入schema.sql所在目录， 创建表
```
mysql --user=dang --password=dang --database=dang < schema.sql
```

#
# 上传题库和用户
```
python updata.py
```

#
# 运行程序
```
python manage.py
```

#
# 开始考试
```
http://IP/
```

#
# 查看成绩
http://IP/score


#
# 加入nginx和supervisor

1 复制conf/nginx.conf到/etc/nginx/nginx.conf
```Bash
sudo cp conf/nginx.conf /etc/nginx/
```

2 复制conf/tornado.conf /etc/supervisor/conf.d/
```Bash
sudp cp conf/tornado.conf /etc/supervisor/conf.d/
```

3 检查supervisor是否成功运行
```Bash
$ sudo supervisorctl 
tornadoes:tornado-8000           RUNNING   pid 6268, uptime 2:17:43
tornadoes:tornado-8001           RUNNING   pid 6269, uptime 2:17:43
tornadoes:tornado-8002           RUNNING   pid 6270, uptime 2:17:43
tornadoes:tornado-8003           RUNNING   pid 6271, uptime 2:17:43
```

4 给予/var/www目录权限
```Bash
chown -R www-data /var/www 
```

5 检查nginx是否成功运行
```
http://IP
```

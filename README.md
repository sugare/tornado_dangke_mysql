python 2.7.12<br/>
tornado 4.4.2<br/>
mysql 5.6<br/>

pip install tornado<br/>
pip install torndb<br/>
pip install xlrd<br/>
pip install xlwt<br/>
pip install futures<br/>
sudo apt-get install python-mysqldb<br/>


# 创建库
CREATE DATABASE dang DEFAULT CHARACTER SET utf8;

# 给予权限
GRANT ALL PRIVILEGES ON dang.* TO 'dang'@'localhost' IDENTIFIED BY 'dang';

# 进入schema.sql坐在目录， 创建表
mysql --user=dang --password=dang --database=dang < schema.sql

# 上传题库和用户
python updata.py

# 运行程序
python manage.py

# 开始考试
http://IP/

# 查看成绩
http://IP/score

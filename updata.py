#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 16-11-30 下午12:08
# @Author  : sugare
# @Site    : 
# @File    : updata.py
# @Software: PyCharm


import xlrd, xlwt, os
from torndb import Connection


# CREATE DATABASE `dang` DEFAULT CHARACTER SET utf8;
db = Connection('127.0.0.1' ,'dang' ,'dang' ,'dang')




def upUsers():         # 上传用户
    data = xlrd.open_workbook(r'static/data/users.xls')
    table = data.sheet_by_index(0)
    nrows = table.nrows
    db.execute('set names utf8;')
    for i in (range(1, nrows + 1)):
        sql = 'insert into users(id,username,password,user)values(%d,"%s","%s","%s")' % (i, str(int(table.row_values(i - 1)[0])), str(int(table.row_values(i - 1)[1])), (table.row_values(i - 1)[2]))
        db.execute(sql)


def upQuestionChoice():
    data = xlrd.open_workbook(r'static/data/question.xlsx')
    table = data.sheet_by_index(0)
    nrows = table.nrows
    db.execute('set names utf8;')
    for i in range(1, nrows + 1):
        if i < 61:
            sql = dict(
                sql1 = 'insert into question(qid,content,answer)values( "%s","%s","%s");' % ("s"+str(i), table.row_values(i - 1)[0], table.row_values(i - 1)[5]),
                sql2 = 'insert into choice(content,mask,ques_id)values( "%s","A","%s");' % (table.row_values(i - 1)[1], "s" + str(i)),
                sql3 = 'insert into choice(content,mask,ques_id)values( "%s","B","%s");' % (table.row_values(i - 1)[2], "s" + str(i)),
                sql4 = 'insert into choice(content,mask,ques_id)values( "%s","C","%s");' % (table.row_values(i - 1)[3], "s" + str(i)),
                sql5 = 'insert into choice(content,mask,ques_id)values( "%s","D","%s");' % (table.row_values(i - 1)[4], "s" + str(i)),
            )

        if i > 60 and i <121:
            sql = dict(
                sql1 = 'insert into question(qid,content,answer)values( "%s","%s","%s");' % ("m"+str(i-60), table.row_values(i - 1)[0], table.row_values(i - 1)[5]),
                sql2 = 'insert into choice(content,mask,ques_id)values( "%s","A","%s");' % (table.row_values(i - 1)[1], "m" + str(i-60)),
                sql3 = 'insert into choice(content,mask,ques_id)values( "%s","B","%s");' % (table.row_values(i - 1)[2], "m" + str(i-60)),
                sql4 = 'insert into choice(content,mask,ques_id)values( "%s","C","%s");' % (table.row_values(i - 1)[3], "m" + str(i-60)),
                sql5 = 'insert into choice(content,mask,ques_id)values( "%s","D","%s");' % (table.row_values(i - 1)[4], "m" + str(i-60)),
            )

        if i > 120:
            sql = dict(
                sql = 'insert into question(qid,content,answer)values( "%s", "%s", "%s")' % ("j"+str(i-120), table.row_values(i - 1)[0], table.row_values(i - 1)[5])
            )

        for data in sql.values():
            db.execute(data)


def upSurvey():
    data = xlrd.open_workbook(r'static/data/fujia.xls')
    table = data.sheet_by_index(0)
    for i in range(6, 11):
        sql = 'insert into survey(qid,content)values( "%s","%s");' % ('i' + str(int(table.row_values(i - 1)[0])), table.row_values(i - 1)[1])
        db.execute(sql)

def downloadMask():     # 下载成绩单
    workbook = xlwt.Workbook()
    sheet1 = workbook.add_sheet('results', cell_overwrite_ok=True)

    sheet2 = workbook.add_sheet('investigation', cell_overwrite_ok=True)
    sheet2.write(0, 0, u'问题\选项')
    sheet2.write(0, 1, u'A.非常满意')
    sheet2.write(0, 2, u'B.满意')
    sheet2.write(0, 3, u'C.比较满意')
    sheet2.write(0, 4, u'D.一般')
    sheet2.write(0, 5, u'E.不满意')

    for i in range(1, 6):
        a = db.query('select * from survey where qid="%s";' % ('i' + str(i)))
        sheet2.write(i, 0, a[0]['content'])
        sheet2.write(i, 1, a[0]['A'])
        sheet2.write(i, 2, a[0]['B'])
        sheet2.write(i, 3, a[0]['C'])
        sheet2.write(i, 4, a[0]['D'])
        sheet2.write(i, 5, a[0]['E'])

    sheet1.write(0, 0, u'考号')
    sheet1.write(0, 1, u'姓名')
    sheet1.write(0, 2, u'单选')
    sheet1.write(0, 3, u'多选')
    sheet1.write(0, 4, u'判断')
    sheet1.write(0, 5, u'总分')
    sc = db.query('select * from score;')
    n = 0
    for i in sc:
        n += 1
        sheet1.write(n, 0, i['username'])
        sheet1.write(n, 1, i['user'])
        sheet1.write(n, 2, i['single'])
        sheet1.write(n, 3, i['multi'])
        sheet1.write(n, 4, i['judge'])
        sheet1.write(n, 5, i['total'])
    workbook.save(r'%s/static/data/mask.xls' % (os.path.dirname(__file__)))


if __name__ == '__main__':
    upSurvey()
    upQuestionChoice()
    upUsers()
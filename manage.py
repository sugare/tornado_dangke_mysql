#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 16-12-2 上午11:57
# @Author  : sugare
# @Site    : 
# @File    : manage.py
# @Software: PyCharm
import time
import random
import MySQLdb
import os.path
import subprocess
import torndb
import tornado.web
import tornado.httpserver
from updata import downloadMask
from concurrent.futures import ThreadPoolExecutor
import tornado.gen
import Queue
import os
import threading

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="dang database host")
define("mysql_database", default="dang", help="dang database name")
define("mysql_user", default="dang", help="dang database user")
define("mysql_password", default="dang", help="dang database password")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/?', LoginHandler),
            (r'/exam/?', ExamHandler),
            (r'/investigation/?', InvestigationHandler),
            (r'/score/?(.*)', ScoreHandler),
            (r'/logout/?', LogoutHandler),
        ]
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            template_path=os.path.join(os.path.dirname(__file__), 'template'),
            xsrf_cookies=True,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            login_url="/login",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)
        # Have one global connection to the blog DB across all handlers

        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)

        self.createTables()

    def createTables(self):
        try:
            self.db.get("SELECT COUNT(*) from users;")
        except MySQLdb.ProgrammingError:
            subprocess.check_call(['mysql',
                                   '--host=' + options.mysql_host,
                                   '--database=' + options.mysql_database,
                                   '--user=' + options.mysql_user,
                                   '--password=' + options.mysql_password],
                                  stdin=open('schema.sql'))


class BaseHandler(tornado.web.RequestHandler):

    executor = ThreadPoolExecutor(2)






    @property       # 将db方法变为属性
    def db(self):
        return self.application.db

    def query(self, sql):
        sen = self.db.query(sql)
        return sen

    def exesql(self, sql):
        self.db.execute(sql)




    def get_current_user(self):
        user_id = self.get_secure_cookie("username")
        if not user_id:
            return None
        return user_id


class LoginHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render('login.html')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        username = self.get_argument('username', '')
        password = self.get_argument('password', '')
        sql = 'select * from rec where uid = "%s"' % username
        u = yield self.executor.submit(self.query,sql)
        if u:
            self.write(u'您已经提交试卷！')
            self.finish()
        else:
            sql = 'select username,password from users where username="%s" and password="%s";' % (username, password)
            v = yield self.executor.submit(self.query,sql)
            if v:
                self.set_secure_cookie("username", username)
                self.redirect('/exam')
            else:
                self.redirect('/')


class ExamHandler(BaseHandler):
    def quesNum(self,ty):
        if ty == 's' or ty == 'm':
            L = [ str(x) for x in range(1,61) ]
            Q = random.sample(L, 20)
        elif ty == 'j':
            L = [ str(x) for x in range(1,31) ]
            Q = random.sample(L,10)
        elif ty == 'i':
            L = [ str(x) for x in range(1,6) ]
            Q = random.sample(L,5)
        return map(lambda num: ty+num, Q)

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        s = {'rubbish':'s'}
        m = {'rubbish':'m'}
        j = {'rubbish':'j'}
        for i in (s, m, j):
            for k in self.quesNum(i.pop('rubbish')):
                i[k] = dict()
                sql1 = 'select content from question WHERE qid="%s";' % k
                x = yield self.executor.submit(self.query, sql1)
                sql2 = 'select mask, content from choice WHERE ques_id="%s";' % k
                y = yield self.executor.submit(self.query, sql2)
                i[k][x[0]['content']] = y

        self.render('exam.html', user=self.current_user, s_ques=s, m_ques=m, j_ques=j, )

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        s_mask = 0
        m_mask = 0
        j_mask = 0
        total = 0

        def worker(q):
            while True:
                sql = q.get()
                print '%s' % sql
                #self.db.execute(sql)
                q.task_done()


        q = Queue.Queue()
        for i in range(1):
            t = threading.Thread(target=worker, args=(q,))
            t.daemon = True
            t.start()


        self.request.arguments.pop('_xsrf')

        for i in self.request.arguments:
            user_rec = ''.join(self.request.arguments[i])
            sql = 'select answer from question WHERE qid="%s";' % i
            answer = yield self.executor.submit(self.query, sql)
            sql1 = 'insert into rec(uid, qid, rec, ans) VALUES("%s", "%s", "%s", "%s");' % (self.get_secure_cookie('username'), i, user_rec, answer[0]['answer'])
            #q.put(sql1)
            yield self.executor.submit(self.exesql, sql1)
            if user_rec == answer[0]['answer']:
                if 's' in i:
                    s_mask += 2
                elif 'm' in i:
                    m_mask += 2
                else:
                    j_mask += 2


        total = s_mask + m_mask + j_mask
        sql = 'select user from users where username="%s";' % self.get_secure_cookie('username')
        user = yield self.executor.submit(self.query, sql)
        sql2 = 'insert into score(username,user,single,multi,judge,total) VALUES("%s", "%s", %d, %d, %d, %d);' % (self.get_secure_cookie('username'), user[0]['user'], s_mask, m_mask, j_mask, total)
        # q.put(sql2)
        yield self.executor.submit(self.exesql, sql2)
        self.redirect('/investigation')
        # q.join()

class InvestigationHandler(ExamHandler):
    @tornado.gen.coroutine
    def get(self):
        i_ques = {}
        for i in self.quesNum('i'):
            sql = 'select content from survey WHERE qid="%s";' % i
            # q = self.query(sql)
            q = yield self.executor.submit(self.query, sql)
            i_ques[i] = q[0]

        self.render('invest.html', i_ques=i_ques)

    @tornado.gen.coroutine
    def post(self):
        self.request.arguments.pop('_xsrf')
        for i in ('i1', 'i2' ,'i3' ,'i4', 'i5'):
            v = self.get_argument(i,'A')
            sql = 'update survey set %s = %s + 1 WHERE qid="%s";' % (v,v, i)
            yield self.executor.submit(self.exesql, sql)
        self.redirect('/logout')


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("username")
        self.write(u'交卷成功！')
        self.redirect(self.get_argument("next", "/"), )


class ScoreHandler(ExamHandler):
    def get(self, slug=''):
        downloadMask()
        if slug:
            sql = 'select * from rec WHERE uid="%s";' % slug
            s = self.query(sql)
            self.render('score_detail.html', s=s)
        else:
            sql = 'select * from score;'
            s = self.query(sql)
            self.render('score.html', s=s)




def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
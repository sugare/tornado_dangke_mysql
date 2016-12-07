#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 16-12-2 上午11:57
# @Author  : sugare
# @Site    : 
# @File    : manage.py
# @Software: PyCharm
import random
import MySQLdb
import os.path
import subprocess
import torndb
import tornado.web
import tornado.httpserver
from updata import downloadMask

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

        self.maybeCreateTables()

    def maybeCreateTables(self):
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
    @property       # 将db方法变为属性
    def db(self):
        return self.application.db

    def get_current_user(self):
        user_id = self.get_secure_cookie("username")
        if not user_id:
            return None
        return user_id


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.get_argument('username', '')
        password = self.get_argument('password', '')
        u = self.db.query('select * from rec where uid = "%s"' % username)
        if u:
            self.write(u'您已经提交试卷！')
        else:
            sql = 'select username,password from users where username="%s" and password="%s";' % (username, password)
            if self.db.get(sql):
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
    def get(self):
        s = {'rubbish':'s'}
        m = {'rubbish':'m'}
        j = {'rubbish':'j'}
        for i in (s, m, j):
            for k in self.quesNum(i.pop('rubbish')):
                i[k] = dict()
                x = self.db.get('select content from question WHERE qid="%s";' % k)
                y = self.db.query('select mask, content from choice WHERE ques_id="%s";' % k)
                i[k][x['content']] = y

        self.render('exam.html', user=self.current_user, s_ques=s, m_ques=m, j_ques=j, )

    @tornado.web.authenticated
    def post(self):
        s_mask = 0
        m_mask = 0
        j_mask = 0
        total = 0

        self.request.arguments.pop('_xsrf')
        for i in self.request.arguments:
            user_rec = ''.join(self.request.arguments[i])
            answer = self.db.get('select answer from question WHERE qid="%s";' % i)['answer']
            self.db.execute('insert into rec(uid, qid, rec, ans) VALUES("%s", "%s", "%s", "%s");' % (self.get_secure_cookie('username'), i, user_rec, answer))
            if user_rec == answer:
                if 's' in i:
                    s_mask += 2
                elif 'm' in i:
                    m_mask += 2
                else:
                    j_mask += 2

        total = s_mask + m_mask + j_mask
        user = self.db.get('select user from users where username="%s";' % self.get_secure_cookie('username'))['user']
        self.db.execute('insert into score(username,user,single,multi,judge,total) VALUES("%s", "%s", %d, %d, %d, %d);' % (self.get_secure_cookie('username'), user, s_mask, m_mask, j_mask, total))
        self.redirect('/investigation')

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("username")
        self.write(u'交卷成功！')
        self.redirect(self.get_argument("next", "/"), )


class InvestigationHandler(ExamHandler):
    def get(self):
        i_ques = {}
        for i in self.quesNum('i'):
            q = self.db.get('select content from survey WHERE qid="%s";' % i)
            i_ques[i] = q
        self.render('invest.html', i_ques=i_ques)

    def post(self):
        self.request.arguments.pop('_xsrf')
        for i in ('i1', 'i2' ,'i3' ,'i4', 'i5'):
            v = self.get_argument(i,'A')
            self.db.execute('update survey set %s = %s + 1 WHERE qid="%s";' % (v,v, i))
        self.redirect('/logout')


class ScoreHandler(ExamHandler):
    def get(self, slug=''):
        downloadMask()
        if slug == '':
            s = self.db.query('select * from score;')
            self.render('score.html', s=s)
        else:
            s = self.db.query('select * from rec WHERE uid="%s";' % slug)
            self.render('score_detail.html', s=s)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
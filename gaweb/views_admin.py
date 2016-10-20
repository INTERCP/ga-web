#-*- coding: utf-8 -*-
from flask import abort, redirect, url_for, session
from flask.ext.login import LoginManager, current_user, login_user, logout_user

from gaweb import app, db
from gaweb.models import *
from gaweb.functions import *

import urllib, datetime


from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask_admin import helpers, expose

from wtforms import form, fields, validators
from flask_admin.base import AdminIndexView, BaseView

from sqlalchemy.sql.expression import case, func
from datetime import timedelta
from flask.helpers import make_response


import xlsxwriter
from httplib import HTTPResponse


# flask-admin Login User
class AdminUser(db.Model):
    __tablename__ = 'admin'
    idx = db.Column('idx', db.Integer, primary_key=True)
    adminid = db.Column('adminid', db.String(45))
    adminpw = db.Column('adminpw', db.String(255))
    role = db.Column('role', db.String(45))
    camp = db.Column('camp', db.String(45))
    
    def __init__(self, adminid, adminpw, role, camp):
        self.adminid = adminid
        self.adminpw = adminpw
        self.role = role
        self.camp = camp

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return unicode(self.adminid)
    


login_manager = LoginManager()
login_manager.init_app(app)
    
# Create user loader function
@login_manager.user_loader
def load_user(adminid):
    return AdminUser.query.filter(AdminUser.adminid == adminid).first()
    
    
# Admin login form
class LoginForm(form.Form):
    adminid = fields.TextField(u'아이디', validators=[validators.required()])
    adminpw = fields.PasswordField(u'비밀번호', validators=[validators.required()])

    # 메서드 이름 규칙: valdiate_<fieldname>
    def validate_adminid(self, field):
        user = self.get_user()
        
        session['role'] = user.role
        session['camp'] = user.camp
        
        if user is None:
            raise validators.ValidationError('Invalid User')
        
        if not user.adminpw == self.adminpw.data:
            raise validators.ValidationError('Invalid Password') 
        
    def get_user(self):
        return AdminUser.query.filter(AdminUser.adminid == self.adminid.data and AdminUser.adminpw == self.adminpw.data).first()
    
class CancelForm(form.Form):
    cancel_reason = fields.TextAreaField(u'취소사유',validators=[validators.required(u'취소사유를 입력해주세요')])
    '''
    def validate_cancel_reason(self, field):
        if self.cancel_yn.data == None:
            raise validators.ValidationError(u'취소사유를 입력해주세요')
    '''
class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and session['role'] == 'hq'

class ExcelDownloadView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and session['role'] == 'hq'
    
    @expose('/')
    def index(self):
        try:
            import cStringIO as StringIO
        except:
            import StringIO
            
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        query = "SELECT * FROM `2015_ga_member` WHERE `cancel_yn` = 0 ORDER BY `idx` DESC"
        result = db.engine.execute(query)
        
        r = 0
        c = 0
        for colname in result._metadata.keys:
            worksheet.write(r, c, colname)
            c += 1
        r += 1

        row = result.fetchone()
        print result._metadata.keys
        while row != None:
            c = 0
            
            for colname in result._metadata.keys:
                worksheet.write(r, c, getattr(row, colname))
                c += 1
            
            r += 1
            row = result.fetchone()    

        
        workbook.close()
        
        output.seek(0)
        response = make_response(output.read())
        response.headers["Content-Disposition"] = "attachment; filename=member.xlsx"
        return response    

def getQuery(tag):
        
        if tag == 'training':
            return {"query":"SELECT value name, count(*) count, count(amount) r_count, sum(case when attend_yn = '예' then 1 else 0 end) a_count, sum(case when member.job = '목회자' then 1 else 0 end) cnt_pastor, sum(case when member.job = '비목회자' then 1 else 0 end) cnt_nonpastor FROM 2015_ga_member as member, membership WHERE `key` = 'training' AND member.idx = membership.member_idx and member.cancel_yn = 0 GROUP BY value","tag":tag}
        elif tag == 'city':
            return {"query":"SELECT %s name, count(*) count, persontype, count(amount) r_count, sum(case when attend_yn = '예' then 1 else 0 end) a_count, sum(case when job = '목회자' then 1 else 0 end) cnt_pastor, sum(case when job = '비목회자' then 1 else 0 end) cnt_nonpastor FROM 2015_ga_member WHERE cancel_yn = 0 group by %s, persontype" % (tag, tag), "tag":tag }
        else:
            return {"query":"SELECT %s name, count(*) count, count(amount) r_count, sum(case when attend_yn = '예' then 1 else 0 end) a_count, sum(case when job = '목회자' then 1 else 0 end) cnt_pastor, sum(case when job = '비목회자' then 1 else 0 end) cnt_nonpastor FROM 2015_ga_member WHERE cancel_yn = 0 group by %s" % (tag, tag), "tag":tag }
    
class MyAdminIndexView(AdminIndexView):
    
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        
        
        # returns single row
        queries = [
            """
            SELECT COUNT(*) as total, 
            COUNT(amount) as registered, 
            sum(case when job = '목회자' and cancel_yn=0 then 1 else 0 end) t_pastor, 
            sum(case when job = '비목회자' and cancel_yn=0 then 1 else 0 end) t_nonpastor, 
            sum(case when job = '목회자' and amount is not null and cancel_yn=0 then 1 else 0 end) r_pastor, 
            sum(case when job = '비목회자' and amount is not null and cancel_yn=0 then 1 else 0 end) r_nonpastor 
            FROM 2015_ga_member WHERE cancel_yn = 0
            """,
            "SELECT COUNT(*) as t_man, COUNT(amount) as r_man, sum(case when job = '목회자' then 1 else 0 end) cnt_man_p, sum(case when job = '비목회자' then 1 else 0 end) cnt_man_np FROM 2015_ga_member WHERE sex='남' and cancel_yn = 0 and persontype='국내'",
            "SELECT COUNT(*) as t_woman, COUNT(amount) as r_woman, sum(case when job = '목회자' then 1 else 0 end) cnt_woman_p, sum(case when job = '비목회자' then 1 else 0 end) cnt_woman_np FROM 2015_ga_member WHERE sex='여' and cancel_yn = 0 and persontype='국내'",
          
        ]
       
        
        #returns multiple rows
        mqueries = [
            getQuery('sex'),
            getQuery('persontype'),
            getQuery('date_of_arrival'),
            getQuery('date_of_leave'),
            getQuery('mit_yn'),
            getQuery('training'),
            getQuery('city'),
            
        ]
    
        stat = {}
    
        for q in queries:
            result = db.engine.execute(q)
            row = result.fetchone()
            stat.update(dict((col, getattr(row, col)) for col in result._metadata.keys))
    
        for q in mqueries:
            result = db.engine.execute(q['query'])
    
            row = result.fetchone()
            rows = []
            while row != None:
                rows.append(dict((col, getattr(row, col)) for col in result._metadata.keys))
                row = result.fetchone()
            stat[q['tag']] = rows
        
        
        #dates = ['2015-05-20', '2015-05-21', '2015-05-22']
        
        self._template_args['stat'] = stat
        return super(MyAdminIndexView, self).index()
    
    @expose('/login/', methods=['GET', 'POST'])
    def login_view(self):
        
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)
            
        if current_user.is_authenticated:
            return redirect(url_for('.index'))
        
        self._template_args['form'] = form
        self._template_args['link'] = ''
        return super(MyAdminIndexView, self).index()
        
    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))
    
    @expose('/person/<idx>/cancel', methods=['GET','POST'])
    def cancel_person(self, idx):
        form = CancelForm(request.form)
        if helpers.validate_form_on_submit(form):
            member = Member.query.filter(Member.idx == idx).one()
            member.cancel_yn = 1
            member.cancel_reason = form.cancel_reason
            db.session.commit()
            return redirect(url_for('.index'))
        
        
        self._template_args['form'] = form
        return self.render('admin/cancel.html')
    
    @expose('/person/<idx>/delpay')
    def del_payment(self, idx):
        Payment.query.filter(Payment.member_idx == idx).delete()
        db.session.commit()
        
        return redirect(url_for('list.person', idx=idx))
    

class StatView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and session['role'] == 'hq'
    
    @expose('/')
    def index(self):
        # returns single row
        queries = [
            """
            SELECT COUNT(*) as total, 
            COUNT(amount) as registered, 
            sum(case when job = '목회자' and cancel_yn=0 then 1 else 0 end) t_pastor, 
            sum(case when job = '비목회자' and cancel_yn=0 then 1 else 0 end) t_nonpastor, 
            sum(case when job = '목회자' and amount is not null and cancel_yn=0 then 1 else 0 end) r_pastor, 
            sum(case when job = '비목회자' and amount is not null and cancel_yn=0 then 1 else 0 end) r_nonpastor 
            FROM 2015_ga_member WHERE cancel_yn = 0
            """,
            "SELECT COUNT(*) as t_man, COUNT(amount) as r_man, sum(case when job = '목회자' then 1 else 0 end) cnt_man_p, sum(case when job = '비목회자' then 1 else 0 end) cnt_man_np FROM 2015_ga_member WHERE sex='남' and cancel_yn = 0 and persontype='국내'",
            "SELECT COUNT(*) as t_woman, COUNT(amount) as r_woman, sum(case when job = '목회자' then 1 else 0 end) cnt_woman_p, sum(case when job = '비목회자' then 1 else 0 end) cnt_woman_np FROM 2015_ga_member WHERE sex='여' and cancel_yn = 0 and persontype='국내'",
            "SELECT COUNT(*) cnt_attend, SUM(CASE WHEN sex='남' THEN 1 ELSE 0 END) cnt_man_attend, SUM(CASE WHEN sex='여' THEN 1 ELSE 0 END) cnt_woman_attend FROM 2015_ga_member WHERE attend_yn = '예'"
        ] 
        
        

        #returns multiple rows
        mqueries = [
            getQuery('sex'),
            getQuery('persontype'),
            getQuery('date_of_arrival'),
            getQuery('date_of_leave'),
            getQuery('mit_yn'),
            getQuery('training'),
            getQuery('city'),
            {"query":"SELECT `persontype`, `job`, count(*) `cnt`, count(amount) `r_cnt`, sum(case when attend_yn = '예' then 1 else 0 end) `a_cnt` FROM `mcampadm`.`2015_ga_member` WHERE `cancel_yn` = 0 GROUP BY `persontype`, `job`", "tag": "summary"},
            {"query":"SELECT `persontype`, `job`, `date_of_arrival`, count(*) `cnt`, count(amount) `r_cnt`, sum(case when attend_yn = '예' then 1 else 0 end) `a_cnt` FROM `mcampadm`.`2015_ga_member` WHERE `cancel_yn` = 0 GROUP BY `persontype`, `job`, `date_of_arrival`", "tag": "date_of_arrival"},
            {"query":"SELECT `persontype`, `job`, `date_of_leave`, count(*) `cnt`, count(amount) `r_cnt`, sum(case when attend_yn = '예' then 1 else 0 end) `a_cnt` FROM `mcampadm`.`2015_ga_member` WHERE `cancel_yn` = 0 GROUP BY `persontype`, `job`, `date_of_leave`", "tag": "date_of_leave"},
            
        ]
    
        stat = {}
    
        for q in queries:
            result = db.engine.execute(q)
            row = result.fetchone()
            stat.update(dict((col, getattr(row, col)) for col in result._metadata.keys))
    
        for q in mqueries:
            result = db.engine.execute(q['query'])
    
            row = result.fetchone()
            rows = []
            while row != None:
                rows.append(dict((col, getattr(row, col)) for col in result._metadata.keys))
                row = result.fetchone()
            stat[q['tag']] = rows
        
        
        dates = [datetime.date(2015, 5, 20), datetime.date(2015, 5, 21), datetime.date(2015, 5, 22), datetime.date(2015, 5, 23)]
        persontypes = [u'국내', u'해외']
        jobs = [u'목회자', u'비목회자']
        en_name = {u'국내':'dom', u'해외':'intl', u'목회자':'pastor', u'비목회자':'nonpastor'}
        
        stat_total = {}
        for persontype in persontypes:
            stat_total[en_name[persontype]] = dict((en_name[col], {"cnt":0, "r_cnt":0, "a_cnt":0}) for col in jobs)
        
        for row in stat['summary']:
            cnt = row['cnt']
            r_cnt = row['r_cnt']
            job = row['job']
            persontype = row['persontype']
            stat_total[en_name[persontype]][en_name[job]]['cnt'] = row['cnt']
            stat_total[en_name[persontype]][en_name[job]]['r_cnt'] = row['r_cnt']
            stat_total[en_name[persontype]][en_name[job]]['a_cnt'] = row['a_cnt']
        
        stat_doa = {} # date_of_arrive
        stat_dol = {} # date_of_leave
        for date in dates:
            datestr = date.strftime("%Y-%m-%d")
            stat_doa[datestr] = {}
            stat_dol[datestr] = {}
            for persontype in persontypes:
                stat_doa[datestr][persontype] = dict((col, {"cnt":0, "r_cnt":0, "a_cnt":0}) for col in jobs)
                stat_dol[datestr][persontype] = dict((col, {"cnt":0, "r_cnt":0, "a_cnt":0}) for col in jobs)
                
        for row in stat['date_of_arrival']:
            cnt = row['cnt']
            r_cnt = row['r_cnt']
            a_cnt = row['a_cnt']
            job = row['job']
            doa = row['date_of_arrival'].strftime("%Y-%m-%d")
            persontype = row['persontype']
            
            stat_doa[doa][persontype][job]['cnt'] = cnt
            stat_doa[doa][persontype][job]['r_cnt'] = r_cnt
            stat_doa[doa][persontype][job]['a_cnt'] = a_cnt
        
                
        for row in stat['date_of_leave']:
            cnt = row['cnt']
            r_cnt = row['r_cnt']
            a_cnt = row['a_cnt']
            job = row['job']
            dol = row['date_of_leave'].strftime("%Y-%m-%d")
            persontype = row['persontype']
            
            stat_dol[dol][persontype][job]['cnt'] = cnt
            stat_dol[dol][persontype][job]['r_cnt'] = r_cnt
            stat_dol[dol][persontype][job]['a_cnt'] = a_cnt
        
        stat_final = {}
        for date in dates:
            datestr = date.strftime("%Y-%m-%d")
            stat_final[datestr] = {}
            for persontype in persontypes:
                stat_final[datestr][en_name[persontype]] = {}
                for job in jobs:
                    stat_final[datestr][en_name[persontype]][en_name[job]] = {}
                    if date == dates[0]:
                        stat_final[datestr][en_name[persontype]][en_name[job]]['cnt'] = stat_doa[datestr][persontype][job]['cnt']
                        stat_final[datestr][en_name[persontype]][en_name[job]]['r_cnt'] = stat_doa[datestr][persontype][job]['r_cnt']
                        stat_final[datestr][en_name[persontype]][en_name[job]]['a_cnt'] = stat_doa[datestr][persontype][job]['a_cnt']
                    else:
                        yesterday = (date - timedelta(days=1))
                        yesterdaystr = yesterday.strftime("%Y-%m-%d")
                        stat_final[datestr][en_name[persontype]][en_name[job]]['cnt'] = stat_final[yesterdaystr][en_name[persontype]][en_name[job]]['cnt'] - stat_dol[yesterdaystr][persontype][job]['cnt'] + stat_doa[datestr][persontype][job]['cnt']
                        stat_final[datestr][en_name[persontype]][en_name[job]]['r_cnt'] = stat_final[yesterdaystr][en_name[persontype]][en_name[job]]['r_cnt'] - stat_dol[yesterdaystr][persontype][job]['r_cnt'] + stat_doa[datestr][persontype][job]['r_cnt']
                        stat_final[datestr][en_name[persontype]][en_name[job]]['a_cnt'] = stat_final[yesterdaystr][en_name[persontype]][en_name[job]]['a_cnt'] - stat_dol[yesterdaystr][persontype][job]['a_cnt'] + stat_doa[datestr][persontype][job]['a_cnt']

        
        self._template_args['stat'] = stat
        self._template_args['stat_total'] = stat_total
        self._template_args['stat_summary'] = stat_final
        self._template_args['persontypes'] = ['intl', 'dom']
        self._template_args['dates'] = dates
        self._template_args['jobs'] = ['pastor', 'nonpastor']
        self._template_args['en_name'] = en_name
        
        return self.render("admin/more_stat.html")

class GaListView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    @expose('/')
    def list(self):
        if not current_user.is_authenticated:
            return redirect(url_for('admin.login_view'))
    
        if not request.args.get('page') == None:
            page = int("%s" % request.args.get('page'))
            
        else:
            page = 1
            
        if not request.args.get('search') == None:
            search = " AND name='%s'" % request.args.get('search')
        else:
            search = ''
            
        member_view = db.engine.execute("SELECT * FROM 2015_ga_member where cancel_yn=0%s ORDER BY regdate DESC LIMIT %d, %d" % (search, (page-1)*15, 15))
        member_max = db.engine.execute("SELECT count(*) cnt FROM 2015_ga_member where cancel_yn=0%s" % search)
        
        members = []
        row = member_view.fetchone()
        #print member_view._metadata.keys
        while row != None:
            members.append(dict((col, getattr(row, col)) for col in member_view._metadata.keys))
            row = member_view.fetchone()
            
        row2 = member_max.fetchone()
        m_max = int(getattr(row2, 'cnt'))
        page_max = (m_max/15)+1
            
        
        self._template_args['members'] = members    
        self._template_args['page'] = page
        self._template_args['page_max'] = page_max
        
        return self.render('admin/list.html')
    
    @expose('/attend', methods=['POST'])
    def attend(self):
        idx = request.form.get('idx', None)
        member = Member.query.filter(Member.idx == idx).one()
        
        member.attend_yn = not member.attend_yn

        db.session.commit()
        
        return "OK"
        
        
    @expose('/download')
    def download(self):
        try:
            import cStringIO as StringIO
        except:
            import StringIO
            
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        query = "SELECT * FROM `2015_ga_member` WHERE `cancel_yn` = 0 ORDER BY `regdate` DESC"
        result = db.engine.execute(query)
        
        r = 0
        c = 0
        for colname in result._metadata.keys:
            worksheet.write(r, c, colname)
            c += 1
        r += 1
        
        #rows = []
        row = result.fetchone()
        print result._metadata.keys
        while row != None:
            c = 0
            
            for colname in result._metadata.keys:
                worksheet.write(r, c, getattr(row, colname))
                c += 1
            
            r += 1
            row = result.fetchone()    
            #worksheet.write(row, col)
            #rows.append(dict((col, getattr(row,col)) for col in result._metadata.keys))
        
        workbook.close()
        
        output.seek(0)
        response = make_response(output.read())
        response.headers["Content-Disposition"] = "attachment; filename=member.xlsx"
        return response
    
    # 특정 검색조건에 대한 리스트 보기 
    @expose('/<category>/<val>/')
    def list_filter(self, category, val):
        if not current_user.is_authenticated:
            return redirect(url_for('admin.login_view'))
        
        if not request.args.get('page') == None:
            page = int("%s" % request.args.get('page'))
            
        else:
            page = 1
            
        if not request.args.get('search') == None:
            search = " AND name='%s'" % request.args.get('search')
        else:
            search = ''
        
        if val == 'None':
            member_view = db.engine.execute("SELECT * FROM 2015_ga_member WHERE cancel_yn=0 and %s IS NULL%s ORDER BY sex, denomination, date_of_arrival" % (category, search))
            #member_max = db.engine.execute("SELECT count(*) cnt FROM 2015_ga_member WHERE cancel_yn=0 and %s IS NULL%s" % (category, search))
        elif val == '':
            member_view = db.engine.execute("SELECT * FROM 2015_ga_member WHERE cancel_yn=0 and %s = ''%s ORDER BY sex, denomination, date_of_arrival" % (category, search))
            #member_max = db.engine.execute("SELECT count(*) cnt FROM 2015_ga_member WHERE cancel_yn=0 and %s = ''%s" % (category, search))
        else:
            member_view = db.engine.execute("SELECT * FROM 2015_ga_member WHERE cancel_yn=0 and %s = '%s'%s ORDER BY sex, denomination, date_of_arrival" % (category, urllib.unquote(val), search))
            #member_max = db.engine.execute("SELECT count(*) cnt FROM 2015_ga_member WHERE cancel_yn=0 and %s = '%s'%s" % (category, urllib.unquote(val), search))

        members = []
        row = member_view.fetchone()
        while row != None:
            members.append(dict((col, getattr(row, col)) for col in member_view._metadata.keys))
            row = member_view.fetchone()

        page_max = 1
    
        self._template_args['members'] = members
        self._template_args['page'] = page
        self._template_args['page_max'] = page_max  
        
        return self.render('admin/list.html')
    
    
    @expose('/<pastor>/<category>/<val>/')
    def pastors_filter(self, pastor, category, val):
        if not current_user.is_authenticated:
            return redirect(url_for('admin.login_view'))

        if pastor == 'pastor':
            job = '목회자'
        else:
            job = '비목회자'
        
        if not request.args.get('page') == None:
            page = int("%s" % request.args.get('page'))
            
        else:
            page = 1
        
        if not request.args.get('search') == None:
            search = " AND name='%s'" % request.args.get('search')
        else:
            search = ''
        
        
        
        if val == 'None':
            member_view = db.engine.execute("SELECT * FROM 2015_ga_member WHERE cancel_yn=0 and %s IS NULL AND job = '%s'%s ORDER BY sex, denomination, date_of_arrival" % (category, job, search))
            #member_max = db.engine.execute("SELECT count(*) cnt FROM 2015_ga_member WHERE cancel_yn=0 and %s IS NULL%s" % (category, search))
        elif val == '':
            member_view = db.engine.execute("SELECT * FROM 2015_ga_member WHERE cancel_yn=0 and %s = '' AND job = '%s'%s ORDER BY sex, denomination, date_of_arrival" % (category, job, search))
            #member_max = db.engine.execute("SELECT count(*) cnt FROM 2015_ga_member WHERE cancel_yn=0 and %s = ''%s" % (category, search))
        else:
            member_view = db.engine.execute("SELECT * FROM 2015_ga_member WHERE cancel_yn=0 and %s = '%s' AND job = '%s'%s ORDER BY sex, denomination, date_of_arrival" % (category, urllib.unquote(val), job, search))
            #member_max = db.engine.execute("SELECT count(*) cnt FROM 2015_ga_member WHERE cancel_yn=0 and %s = '%s'%s" % (category, urllib.unquote(val), search))
        
        members = []
        row = member_view.fetchone()
        while row != None:
            members.append(dict((col, getattr(row, col)) for col in member_view._metadata.keys))
            row = member_view.fetchone()
    
        #row2 = member_max.fetchone()
        #m_max = int(getattr(row2, 'cnt'))
        #page_max = (m_max/15)+1
    
        self._template_args['members'] = members
        self._template_args['page'] = page
        #self._template_args['page_max'] = page_max  
        self._template_args['page_max'] = 1
        return self.render('admin/list.html')
    
    @expose('/person/<idx>/')
    def person(self, idx):
        try:
            payment = Payment.query.filter(Payment.member_idx == idx).one()
        except NoResultFound:
            payment = None
        
        try:
            member = Member.query.filter(Member.idx == idx).one()
        except NoResultFound:
            member = None
            
        membership = getMembership(Membership.query.filter(Membership.member_idx == idx).all())
        
        room_query = db.engine.execute("SELECT * FROM 2015_ga_room")
        
        rooms = []
        
        row2 = room_query.fetchone()
        while row2 != None:
            rooms.append(dict((col, getattr(row2, col)) for col in room_query._metadata.keys))
            row2 = room_query.fetchone()
            
        self._template_args['rooms'] = rooms
        
        self._template_args['payment'] = payment
        self._template_args['member'] = member
        self._template_args['membership'] = membership
        self._template_args['role'] = session['role']
        return self.render('admin/person.html')

    @expose('/person/<idx>/pay', methods=['POST'])
    def person_pay(self, idx):
        amount = request.form.get('amount')
        complete = request.form.get('complete')
        claim = request.form.get('claim')
        staff_name = request.form.get('staff_name')
        code = request.form.get('code')
        
        try:
            payment = Payment.query.filter(Payment.member_idx == idx).one()
            payment.amount = amount
            payment.complete = complete
            payment.claim = claim
            payment.staff_name = staff_name
            payment.code = code
            
            db.session.commit()
        except NoResultFound:
            payment = Payment(idx, amount, complete, claim, staff_name, datetime.datetime.today(), code)
            db.session.add(payment)
            db.session.commit()
            
        return redirect(url_for('list.person', idx = idx))
    
    @expose('/person/<idx>/edit/')
    def person_edit(self, idx):
        try:
            member = Member.query.filter(Member.idx == idx).one()
        except NoResultFound:
            member = None
            
        membership = getMembership(Membership.query.filter(Membership.member_idx == idx).all())
        
        self._template_args['member'] = member
        self._template_args['membership'] = membership
        return self.render('admin/person_edit.html')
    
    @expose('/person/<idx>/edit/', methods=['POST'])
    def person_edit_proc(self, idx):
        camp_idx = getCampIdx('ga')
        formData = getIndividualFormData()
        if editIndividual(camp_idx, idx, formData):
            return redirect(url_for('list.person', idx = idx))
        else:
            abort(404)
                
        
class GaChildrenListView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    @expose('/')
    def chldrenlist(self):
        if not current_user.is_authenticated:
            return redirect(url_for('admin.login_view'))
        
        member_view = db.engine.execute("SELECT * FROM 2015_ga_member where cancel_yn=0 and children is not null ORDER BY regdate DESC")
        
        members = []
        row = member_view.fetchone()
        while row != None:
            members.append(dict((col, getattr(row, col)) for col in member_view._metadata.keys))
            row = member_view.fetchone()
            
        self._template_args['members'] = members    
        
        return self.render('admin/children_list.html')   
    
    
class GaRoomView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and session['role'] == 'hq'
    
    @expose('/', methods=['GET'])
    def list(self):
        orderby = 'city'
        filter = ''
        filterby = ''
        filterquery = ''

        if not request.args.get('orderby') == None:
            orderby = ", %s" % request.args.get('orderby')
            
        if request.args.get('filter') != None:
            filterquery = urllib.unquote(request.args.get('filter'))
            

        member_view = db.engine.execute("SELECT * FROM 2015_ga_member where cancel_yn=0 and persontype='국내' and (complete=2 or complete=1) and room_idx is null%s ORDER BY sex, job, city" % (filterquery))
        
        members = []
        row = member_view.fetchone()
        while row != None:
            members.append(dict((col, getattr(row, col)) for col in member_view._metadata.keys))
            row = member_view.fetchone()
        
        self._template_args['members'] = members    
            
        room_query = db.engine.execute("SELECT * FROM 2015_ga_room")
        
        rooms = []
        
        row2 = room_query.fetchone()
        while row2 != None:
            rooms.append(dict((col, getattr(row2, col)) for col in room_query._metadata.keys))
            row2 = room_query.fetchone()
            
        self._template_args['rooms'] = rooms
        
        return self.render('admin/roomasign_list.html')
    
    @expose('/assign', methods=['GET'])
    def assign_single(self):
        idx = request.args.get('idx', None)
        member_idx = request.args.get('member_idx', None)
        
        
        member = Member.query.filter(Member.idx == member_idx).one()
        member.room_idx = idx
        
        db.session.commit()
        
        return redirect(url_for('list.person', idx=member_idx))
    
    @expose('/<idx>', methods=['POST'])
    def assign(self, idx):
        formdata = request.form
        
        for f in formdata:
            
            member_idx = f
            member = Member.query.filter(Member.idx == member_idx).one()
            member.room_idx = idx
                
        db.session.commit()
        
        return redirect(url_for('room.list'))
    
    
    
    
class GaRoomStatusView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and session['role'] == 'hq'
    
    @expose('/', methods=['GET'])
    def index(self):
        
        members = []
        self._template_args['members'] = members    
            
        room_query = db.engine.execute("SELECT * FROM 2015_ga_room")
        
        rooms = []
        
        row2 = room_query.fetchone()
        while row2 != None:
            rooms.append(dict((col, getattr(row2, col)) for col in room_query._metadata.keys))
            row2 = room_query.fetchone()
            
        self._template_args['rooms'] = rooms
        
        return self.render('admin/room_status.html')
    
    
    
    @expose('/<idx>/', methods=['GET', 'POST'])
    def members(self, idx):
        member_view = db.engine.execute("SELECT * FROM 2015_ga_member where room_idx = %s ORDER BY regdate DESC" % idx)
        
        members = []
        row = member_view.fetchone()
        while row != None:
            members.append(dict((col, getattr(row, col)) for col in member_view._metadata.keys))
            row = member_view.fetchone()
            
        self._template_args['members'] = members    
            
        room_query = db.engine.execute("SELECT * FROM 2015_ga_room")
        
        rooms = []
        
        row2 = room_query.fetchone()
        while row2 != None:
            rooms.append(dict((col, getattr(row2, col)) for col in room_query._metadata.keys))
            row2 = room_query.fetchone()
            
        self._template_args['rooms'] = rooms
        
        return self.render('admin/room_status.html')
    
    @expose('/<idx>/delete', methods=['POST'])
    def delete(self, idx):
        formdata = request.form
        
        for f in formdata:
            member_idx = f
            member = Member.query.filter(Member.idx == member_idx).one()
            member.room_idx = None
            
        db.session.commit()
        
        return redirect(url_for('.members', idx=idx))
    
class GaStatView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    
    @expose("/")
    def index(self):
        # returns single row
        queries = [
            
            
        ]
    
        #returns multiple rows
        mqueries = [
            
            getQuery('denomination'),
            getQuery('city'),
            getQuery('training'),
            
            #getQuery('regdate'),
        ]
    
        stat = {}
    
        for q in queries:
            result = db.engine.execute(q)
            row = result.fetchone()
            stat.update(dict((col, getattr(row, col)) for col in result._metadata.keys))
    
        for q in mqueries:
            result = db.engine.execute(q['query'])
    
            row = result.fetchone()
            rows = []
            while row != None:
                rows.append(dict((col, getattr(row, col)) for col in result._metadata.keys))
                row = result.fetchone()
            stat[q['tag']] = rows
        
        
        
        self._template_args['stat'] = stat
        return self.render("admin/stat.html")
    
admin = Admin(app, u'GA어드민', index_view=MyAdminIndexView(name=u'홈'), base_template='admin/my_master.html')
admin.add_view(GaListView(name=u'전체리스트', endpoint='list'))
admin.add_view(GaRoomView(name=u'숙소배치', endpoint='room', category=u'숙소'))
admin.add_view(GaRoomStatusView(name=u'숙소현황', endpoint='room/status', category=u'숙소'))
admin.add_view(MyModelView(Room, db.session, endpoint='room/setting', name=u'건물셋팅', category=u'숙소'))
admin.add_view(MyModelView(Roomsetting, db.session, endpoint='room/camp-setting', name=u'캠프숙소셋팅', category=u'숙소'))
admin.add_view(StatView(name=u'통계'))
admin.add_view(GaChildrenListView(name=u'동반자녀리스트', endpoint='children/list'))
admin.add_view(ExcelDownloadView(name=u'엑셀다운로드', endpoint='download'))

@app.route('/ga/admin/login')
@app.route('/ga/admin/')
def admin_home():
    return redirect(url_for('admin.index'))

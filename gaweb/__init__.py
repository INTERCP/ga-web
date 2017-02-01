# -*-coding:utf-8-*-
import sys
import os
import jinja2
from flask import Flask


reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')


# from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.jinja_loader = jinja2.FileSystemLoader(tmpl_dir)
app.secret_key = 'r&rbtrtk3hd36u#9k=8cb*!m@8o1t)zp=mws#s&a!jvvty9yis'

# import config
# Database initialization
# app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
# db = SQLAlchemy(app)

# admin 로그인 정보
app.config['ADMIN_ID'] = 'gaadmin'
app.config['ADMIN_PW'] = 'gabtj'

# 지부 로그인 정보
app.config['JIBU_ID'] = 'gajibu'
app.config['JIBU_PW'] = 'btj1040'

# add views
import gaweb.views

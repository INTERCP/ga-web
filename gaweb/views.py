#-*- coding: utf-8 -*-
from flask import render_template, abort, redirect, url_for, session, flash
from jinja2 import TemplateNotFound

from gaweb import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ga/', defaults={'page':'index', 'lang':None})
@app.route('/ga/<page>', defaults={'lang':None})
@app.route('/ga/<lang>/<page>')
def show(page, lang):
    try:
        if lang == None:
            return render_template('ga/%s.html' % page)
        elif lang == 'en':
            return render_template('ga/en/%s.html' % page)
    except TemplateNotFound:
        abort(404)
        
@app.route('/ga/logout')
def logout():
    session.clear()
    flash('정상적으로 로그아웃 되었습니다.')
    return redirect(url_for('show'))
    
# 개인신청 관련된 로직과 단체신청 관련 로직을 분리하여 관리
import gaweb.views_individual
import gaweb.views_admin


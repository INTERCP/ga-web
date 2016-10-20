#-*- coding: utf-8 -*-
from flask import render_template, abort, redirect, url_for, flash, session
from sqlalchemy.orm.exc import NoResultFound

from gaweb import app, db
from gaweb.models import *
from gaweb.functions import *

import datetime, hashlib

'''

C R E A T E 생성 관련

'''

    
# 개인 신청서 데이터베이스에 저장, TODO 서버단 폼검증
@app.route('/ga/registration', methods=['POST'], defaults={'lang':None})
@app.route('/ga/<lang>/registration', methods=['POST'])
def reg_individual_proc(lang):
    camp_idx = getCampIdx('ga')
    # userid = request.form.get('userid', None)
    name = request.form.get('name', None)
    contact = request.form.get('contact', None)
    
    # 프론트단 폼검증을 통과하였으나 백엔드에서 이름과 연락처가 중복될 경우 Forbidden발생
    if Member.query.filter(Member.camp_idx == camp_idx, Member.name == name, Member.contact == contact, Member.cancel_yn == False).count() > 0:
        #abort(403) # TODO 나중에 오류 페이지를 보여주도록 수정한다
        flash('이미 이름과 연락처가 동일한 신청서가 접수되었습니다.')
        return redirect(url_for('show', lang=lang))
    
    formData = getIndividualFormData()
    regIndividual(camp_idx, formData)
    
    flash('신청이 완료되었습니다.')
    return redirect(url_for('show', lang=lang))
    

'''

R E T R I V E 조회 관련

'''

# 개인 조회하기 - 이메일 및 비밀번호 체크
@app.route('/ga/check', methods=['POST'], defaults={'lang':None})
@app.route('/ga/<lang>/check', methods=['POST'])
def check_individual(lang):
    campidx = getCampIdx('ga')
    name = request.form.get('name', None)
    contact = request.form.get('contact', None)
    pwd = hashlib.sha224(request.form.get('pwd', None)).hexdigest()
    
    try:
        member = Member.query.filter(Member.camp_idx == campidx, Member.name == name, Member.contact == contact, Member.cancel_yn == False).one()
        
        if member.pwd == pwd:
            session['type'] = '개인'
            session['member_idx'] = member.idx
            return redirect(url_for('show_individual', idx=member.idx, lang=lang))
        else:
            flash('조회 실패 - 일치하는 신청자 정보를 찾을 수 없습니다.')
            
    except NoResultFound:
        flash('조회 실패 - 일치하는 신청자 정보를 찾을 수 없습니다.')
        
    return redirect(url_for('show', page='check', lang=lang))

# 개인 조회하기 - 개인 정보 보여주기
@app.route('/ga/reginfo/<idx>/', defaults={'lang':None})
@app.route('/ga/<lang>/reginfo/<idx>/')
def show_individual(idx, lang):
    
    campidx = getCampIdx('ga')
    
    try:
        member_view = db.engine.execute("SELECT * FROM 2015_ga_member WHERE idx = %s" % idx)
        row = member_view.fetchone()
        member = dict((col, getattr(row, col)) for col in member_view._metadata.keys)
        
        
        #member = member_view.query.filter(member_view.idx == idx).one()
        # area_name = getAreaName(member.area_idx)
        
        # 세션 처리
        
        if 'type' in session and session['type'] == '개인' and 'member_idx' in session:
            if member['idx'] == session['member_idx']:
                if lang == None:
                    return render_template('/ga/reginfo.html', member=member)
                elif lang == 'en':
                    return render_template('/ga/en/reginfo.html', member=member)
            
        flash("세션이 만료되었습니다. 다시 로그인해주시기 바랍니다.")
        
        # return render_template('/ga/reginfo.html', member=member)
    except NoResultFound:
        flash('조회 실패 - 일치하는 신청자 정보를 찾을 수 없습니다.')
        
    return redirect(url_for('show'))
   
    
'''

U P D A T E 수정 관련

'''

# 개인 수정하기
@app.route('/ga/reginfo/<idx>/edit', defaults={'lang':None})
@app.route('/ga/<lang>/reginfo/<idx>/edit')
def edit_individual(idx, lang):
    
    area_list = getAreaList('ga')
    # date_select_list = getDateSelectList()
    
    try:
        member = Member.query.filter(Member.idx == idx).one()
        membership = getMembership(Membership.query.filter(Membership.member_idx == idx).all())

        # 세션 처리
        if 'type' in session and session['type'] == '개인' and 'member_idx' in session:
            if member.idx == session['member_idx']:
                if lang == None:
                    return render_template('/ga/registration_edit.html', member=member, membership=membership)
                elif lang == 'en':
                    return render_template('/ga/en/registration_edit.html', member=member, membership=membership)
            
        flash("세션이 만료되었습니다. 다시 로그인해주시기 바랍니다.")
    except NoResultFound:
        flash('조회 실패 - 일치하는 신청자 정보를 찾을 수 없습니다.')
        
    return redirect(url_for('show', page='check', lang=lang))
        
# 개인 수정내용 데이터베이스에 적용
@app.route('/ga/reginfo/<idx>/edit', methods=['POST'], defaults={'lang':None})
@app.route('/ga/<lang>/reginfo/<idx>/edit', methods=['POST'])
def edit_individual_proc(idx, lang):
    
    camp_idx = getCampIdx('ga')
    formData = getIndividualFormData()
    if editIndividual(camp_idx, idx, formData):
        flash('신청서 수정이 완료되었습니다.')
        return redirect(url_for('show_individual', idx=idx, lang=lang))
    else:
        abort(404)
        

'''

D E L E T E 삭제 관련
(단 엄밀하게 따지면 UPDATE임. 표면적으로 DELETE의 기능을 함)

'''        

# 개인 신청 취소
@app.route('/ga/reginfo/<idx>/cancel', defaults={'lang':None})
@app.route('/ga/<lang>/reginfo/<idx>/cancel')
def cancel_individual(idx, lang):
    try:
        member = Member.query.filter(Member.idx == idx).one()
        
        # 세션 처리
        if 'type' in session and session['type'] == '개인' and 'member_idx' in session:
            if member.idx == session['member_idx']:
                if lang == None:
                    return render_template("/ga/cancel.html")
                elif lang == 'en':
                    return render_template("/ga/en/cancel.html")
                
        flash("세션이 만료되었습니다. 다시 로그인해주시기 바랍니다.")
    except NoResultFound:
        flash('조회 실패 - 일치하는 신청자 정보를 찾을 수 없습니다.')
        
    return redirect(url_for('show', page='check', lang=lang))    
        
    
@app.route('/ga/reginfo/<idx>/cancel', methods=['POST'], defaults={'lang':None})
@app.route('/ga/<lang>/reginfo/<idx>/cancel', methods=['POST'])

def cancel_individual_proc(idx, lang):
    cancel_reason = request.form.get('cancel_reason', None)
    
    member = Member.query.filter(Member.idx == idx).one()
    member.cancel_yn = True
    member.cancel_reason = cancel_reason
    member.canceldate = datetime.datetime.today()
    
    db.session.commit()
    
    flash('신청이 정상적으로 취소되었습니다.')
    return redirect(url_for('show', lang=lang))
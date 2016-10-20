#-*- coding: utf-8 -*-
from flask import request

from gaweb import app, db
from gaweb.models import *
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound

import json, datetime, hashlib

# 연도, 텀, 캠프 코드를 입력하면 camp_idx를 반환해줌
def getCampIdx(camp):
    return Camp.query.filter(Camp.year == 2015).filter(Camp.term == 1).filter(Camp.code == camp).one().idx

# 특정 캠프에 대한 지부 리스트를 반환해줌
def getAreaList(camp):
    return Area.query.filter(or_(Area.camp == '*', Area.camp.like('%%%s%%' % camp))).order_by(Area.type.asc(), Area.name.asc()).all()

# 특정 area_idx에 대한 지부 이름 반환
def getAreaName(area_idx):
    return Area.query.filter(Area.idx == area_idx).one().name

# 생년월일 form을 위한 날자 리스트를 반환
def getDateSelectList():
    
    # 연도 리스트를 생성, 1900년 부터 2015년 까지
    yr_list = []
    for i in range(2016, 1900, -1):
        yr_list.append("%d" % i)
        
    # 월 리스트를 생성 1월 부터 12월 까지
    m_list = []
    for i in range(1, 13):
        m_list.append("%02d" % i)
        
    # 일 리스트를 생성 1일 부터 31일 까지
    d_list = []
    for i in range(1, 32):
        d_list.append("%02d" % i)
        
    date_select_list = {}
    
    date_select_list['yr_list'] = yr_list
    date_select_list['m_list'] = m_list
    date_select_list['d_list'] = d_list
    
    return date_select_list

# base query type의 membership list를 넘겨주면 dictionary type으로 반환해줌
def getMembership(membership_list):
    
    membership = {'training':[]}
    #membership['training'] = []
    
    for m in membership_list:
        
        if m.key == 'training':
            membership[m.key].append(m.value)
        else:
            membership[m.key] = m.value
            
    return membership


'''

I N D I V I D U A L 개인 신청 관련

'''


# add 또는 edit 시에 넘겨주는 form data를 dictionary 타입으로 반환해준다.
# regIndividual함수와 editIndividual함수에서 이 함수를 사용함
def getIndividualFormData():
    formData = {}
    
    pwd = request.form.get('pwd', None)
    if pwd != None:
        formData['pwd'] = hashlib.sha224(pwd).hexdigest()
    else:
        formData['pwd'] = None
    formData['name'] = request.form.get('name', None)
    formData['enname'] = request.form.get('enname', None)
    formData['contact'] = request.form.get('contact', None)
    formData['church'] = request.form.get('church', None)
    formData['sex'] = request.form.get('sex', None)
    formData['mit_yn'] = request.form.get('mit_yn', 0)
    formData['persontype'] = request.form.get('persontype', None)
    formData['fullcamp_yn'] = request.form.get('fullcamp_yn', 0)
    formData['date_of_arrival'] = request.form.get('date_of_arrival', None)
    formData['date_of_leave'] = request.form.get('date_of_leave', None)
    formData['language'] = request.form.get('language', '필요 없음')
    formData['memo'] = request.form.get('memo', None)
    
    formData['job'] = request.form.get('job', None)
    formData['denomination'] = request.form.get('denomination', None)
    formData['churchaddr'] = request.form.get('churchaddr', None)
    formData['city'] = request.form.get('city', None)
    formData['children'] = request.form.get('children', None)
    
    formData['training'] = request.form.getlist('training', None)
    formData['none'] = request.form.get('none', None)
    
    
    return formData

# 개인 신청 등록 Process
def regIndividual(camp_idx, formData):
    member = Member(camp_idx, None, formData['pwd'], formData['name'], None, formData['contact'], formData['church'], None, formData['sex'], None, formData['mit_yn'], 0, None, formData['persontype'], formData['fullcamp_yn'], formData['date_of_arrival'], formData['date_of_leave'], formData['language'], None, datetime.datetime.today(), None, 0, None, formData['memo'])
    
    db.session.add(member)
    db.session.commit()
    
    # 방금 추가한 신청자의 member_idx를 다시 불러옴
    member_idx = Member.query.filter(Member.camp_idx == camp_idx, Member.name == formData['name'], Member.contact == formData['contact'], Member.cancel_yn == False).one().idx
    
    membership_keys = ['job', 'denomination', 'churchaddr', 'city', 'children', 'enname']
    
    for key in membership_keys:
        if key in formData and formData[key] != '' and formData[key] != None:
            temp_membership = Membership(camp_idx, member_idx, key, formData[key])
            db.session.add(temp_membership)
    
    # 컨퍼런스 참여 경로
    if 'training' in formData:
        for t in formData['training']:
            t_membership = Membership(camp_idx, member_idx, 'training', t)
            db.session.add(t_membership)
        
    if 'none' in formData and formData['none'] != None:
        none_membership = Membership(camp_idx, member_idx, 'training', formData['none'])
        db.session.add(none_membership)
    
    db.session.commit()
    
# 개인 신청 수정 Process
def editIndividual(camp_idx, member_idx, formData):
    
    try:
        member = Member.query.filter(Member.idx == member_idx).one()
        membership = getMembership(Membership.query.filter(Membership.member_idx == member_idx).all())
        
        
        
        
        if formData['pwd'] != '' and formData['pwd'] != None:
            member.pwd = formData['pwd']
        
        member.name = formData['name']
        #member.area_idx = formData['area_idx']
        member.contact = formData['contact']
        member.church = formData['church']
        #member.birth = formData['birth']
        member.sex = formData['sex']
        #member.bus_yn = formData['bus_yn']
        member.mit_yn = formData['mit_yn']
        #member.newcomer_yn = formData['newcomer_yn']
        member.persontype = formData['persontype']
        member.fullcamp_yn = formData['fullcamp_yn']
        member.date_of_arrival = formData['date_of_arrival']
        member.date_of_leave = formData['date_of_leave']
        member.language = formData['language']
        member.memo = formData['memo']
        #member.group_idx = group_idx
        

        membership_keys = ['job', 'denomination', 'churchaddr', 'city', 'children', 'enname']
        
        for key in membership_keys:
            if key in formData and formData[key] != '' and formData[key] != None:
                if key not in membership:
                    temp_membership = Membership(camp_idx, member_idx, key, formData[key])
                    db.session.add(temp_membership)
                elif membership[key]  != formData[key]:
                    temp_membership = Membership.query.filter(Membership.member_idx == member_idx, Membership.key == key).one()
                    temp_membership.value = formData[key]

        
        
        
        Membership.query.filter(Membership.member_idx == member_idx, Membership.key == 'training').delete()
        
        
        # 컨퍼런스 참여 경로
        if 'training' in formData:
            for t in formData['training']:
                t_membership = Membership(camp_idx, member_idx, 'training', t)
                db.session.add(t_membership)

        if 'none' in formData and formData['none'] != None:
            none_membership = Membership(camp_idx, member_idx, 'training', formData['none'])
            db.session.add(none_membership)
        
        db.session.commit()
        return True
    except NoResultFound:
        return False

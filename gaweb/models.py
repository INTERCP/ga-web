#-*-coding:utf-8-*-
from gaweb import db

# Database Model Declaration
# 지부
class Area(db.Model):
    idx = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    type = db.Column(db.String(45))
    camp = db.Column(db.String(45))
    member = db.relationship('Member', backref='area', lazy='dynamic')
    
    def __init__(self, name, type, camp="*"):
        self.name = name
        self.type = type
        self.camp = camp
        
    def __repr__(self):
        return self.name    
    
# 캠프 구분
class Camp(db.Model):
    idx = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(45))
    year = db.Column(db.Integer)
    term = db.Column(db.Integer)
    startday = db.Column(db.DateTime)
    campday = db.Column(db.Integer)
    name = db.Column(db.String(45))
    member = db.relationship('Member', backref='camp', lazy='dynamic')
    roomsetting = db.relationship('Roomsetting', backref='camp', lazy='dynamic')
    
    def __init__(self, code, year, term, startday, campday, name):
        self.code = code
        self.year = year
        self.term = term
        self.startday = startday
        self.campday = campday
        self.name = name
        
    def __repr__(self):
        return ("%d_%d_%s") % (self.year, self.term, self.name)

# 단체
class Group(db.Model):
    idx = db.Column(db.Integer, primary_key=True)
    camp_idx = db.Column(db.Integer, db.ForeignKey('camp.idx'))
    name = db.Column(db.String(100))
    groupid = db.Column(db.String(45))
    pwd = db.Column(db.String(100))
    leadername = db.Column(db.String(45))
    leadercontact = db.Column(db.String(45))
    leaderjob = db.Column(db.String(45))
    area_idx = db.Column(db.Integer, db.ForeignKey('area.idx'))
    mem_num = db.Column(db.Integer)
    grouptype = db.Column(db.String(45))
    regdate = db.Column(db.DateTime)
    canceldate = db.Column(db.DateTime)
    cancel_yn = db.Column(db.Boolean)
    cancel_reason = db.Column(db.Text)
    memo = db.Column(db.Text)
    
    def __init__(self, camp_idx, name, groupid, pwd, leadername, leadercontact, leaderjob, area_idx, mem_num, grouptype, regdate, canceldate, cancel_yn, cancel_reason, memo):
        self.camp_idx = camp_idx
        self.name = name
        self.groupid = groupid
        self.pwd = pwd
        self.leadername = leadername
        self.leadercontact = leadercontact
        self.leaderjob = leaderjob
        self.area_idx = area_idx
        self.mem_num = mem_num
        self.grouptype = grouptype
        self.regdate = regdate
        self.canceldate = canceldate
        self.cancel_yn = cancel_yn
        self.cancel_reason = cancel_reason
        self.memo = memo
    
# 개인 신청자
class Member(db.Model):
    idx = db.Column(db.Integer, primary_key=True)
    camp_idx = db.Column(db.Integer, db.ForeignKey('camp.idx'))
    userid = db.Column(db.String(100))
    pwd = db.Column(db.String(100))
    name = db.Column(db.String(45, convert_unicode=True))
    area_idx = db.Column(db.Integer, db.ForeignKey('area.idx'))
    contact = db.Column(db.String(45))
    church = db.Column(db.String(45))
    birth = db.Column(db.String(45))
    sex = db.Column(db.String(1))
    bus_yn = db.Column(db.Boolean)
    mit_yn = db.Column(db.Boolean)
    attend_yn = db.Column(db.Boolean)
    newcomer_yn = db.Column(db.Boolean)
    persontype = db.Column(db.String(45, convert_unicode=True))
    fullcamp_yn = db.Column(db.Boolean)
    date_of_arrival = db.Column(db.DateTime)
    date_of_leave = db.Column(db.DateTime)
    language = db.Column(db.String(45, convert_unicode=True))
    group_idx = db.Column(db.Integer)
    regdate = db.Column(db.DateTime)
    canceldate = db.Column(db.DateTime)
    cancel_yn = db.Column(db.Boolean)
    cancel_reason = db.Column(db.Text(convert_unicode=True))
    memo = db.Column(db.Text(convert_unicode=True))
    room_idx = db.Column(db.Integer, db.ForeignKey('room.idx'))
    
    membership = db.relationship('Membership', backref='member', lazy='dynamic')
    
    def __init__(self, camp_idx, userid, pwd, name, area_idx, contact, church, birth, sex, bus_yn, mit_yn, attend_yn, newcomer_yn, persontype, fullcamp_yn, date_of_arrival, date_of_leave, language, group_idx, regdate, canceldate, cancel_yn, cancel_reason, memo):
        self.camp_idx = camp_idx
        self.userid = userid
        self.pwd = pwd
        self.name = name
        self.area_idx = area_idx
        self.contact = contact
        self.church = church
        self.birth = birth
        self.sex = sex
        self.bus_yn = bus_yn
        self.mit_yn = mit_yn
        self.attend_yn = attend_yn
        self.newcomer_yn = newcomer_yn
        self.persontype = persontype
        self.fullcamp_yn = fullcamp_yn
        self.date_of_arrival = date_of_arrival
        self.date_of_leave = date_of_leave
        self.language = language
        self.group_idx = group_idx
        self.regdate = regdate
        self.canceldate = canceldate
        self.cancel_yn = cancel_yn
        self.cancel_reason = cancel_reason
        self.memo = memo
        
    def __repr__(self):
        #area = Area.query.filter(Area.idx == self.area_idx).one()
        #return ("%s %s") % (area, self.name)
        return self.name
    
#개인신청자 활동내용
class Membership(db.Model):
    idx = db.Column(db.Integer, primary_key=True)
    camp_idx = db.Column(db.Integer, db.ForeignKey('camp.idx'))
    member_idx = db.Column(db.Integer, db.ForeignKey('member.idx'))
    key = db.Column(db.String(100))
    value = db.Column(db.String(100))
    
    def __init__(self, camp_idx, member_idx, key, value):
        self.camp_idx = camp_idx
        self.member_idx = member_idx
        self.key = key
        self.value = value
        
# 재정처리
class Payment(db.Model):
    idx = db.Column(db.Integer, primary_key=True)
    member_idx = db.Column(db.Integer, db.ForeignKey('member.idx'))
    amount = db.Column(db.Integer)
    complete = db.Column(db.Integer)
    claim = db.Column(db.Text)
    staff_name = db.Column(db.String(45))
    paydate = db.Column(db.DateTime)
    code = db.Column(db.String(45))
    
    def __init__(self, member_idx, amount, complete, claim, staff_name, paydate, code):
        self.member_idx = member_idx
        self.amount = amount
        self.complete = complete
        self.claim = claim
        self.staff_name = staff_name
        self.paydate = paydate
        self.code = code
        
        
# 숙소
class Room(db.Model):
    idx = db.Column(db.Integer, primary_key=True)
    building = db.Column(db.String(45))
    number = db.Column(db.String(45))
    
    roomsetting = db.relationship('Roomsetting', backref='room', lazy='dynamic')
    member = db.relationship('Member', backref='room', lazy='dynamic')
    
    def __repr__(self):
        return "%s %s" % (self.building, self.number) 
    
class Roomsetting(db.Model):
    idx = db.Column(db.Integer, primary_key=True)
    camp_idx = db.Column(db.Integer, db.ForeignKey('camp.idx'))
    room_idx = db.Column(db.Integer, db.ForeignKey('room.idx'))
    cap = db.Column(db.Integer)
    memo = db.Column(db.Text)
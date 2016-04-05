from . import db  
class myprofile(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    age = db.Column(db.Integer)
    sex = db.Column(db.String(8))
    
    
    def __init__(self, firstname, lastname, email, password, age, sex):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.age = age
        self.sex = sex
    
    
    def is_authenticated(self):
        return True
        
        
    def is_active(self):
        return True
        
        
    def is_anonymous(self):
        return False
        
        
    def get_id(self):
        return unicode(self.userid)
        
        
    def __repr__(self):
        return '<User %r>' % self.userid


class mywish(db.Model):
    wishid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('myprofile.userid'))
    title = db.Column(db.String(100))
    description = db.Column(db.String(500))
    description_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    
    
    def __init__(self, userid, title, description, description_url):
        self.userid = userid
        self.title = title
        self.description = description
        self.description_url = description_url
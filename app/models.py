from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin




class Test(db.Model):
    ID_Test=db.Column(db.Integer,primary_key=True)
    Value=db.Column(db.String(64))

    def __repr__(self):
        return '<Test {}>'.format(self.Value)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.String(50))
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.fullname)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address_raw = db.Column(db.String(100))
    address_clean = db.Column(db.String(100))
    coordinates = db.Column(db.String(100))
    indications=db.relationship('Indication',backref='device',lazy=True)

    def __repr__(self):
        return '<Device {}>'.format(self.address_raw)

    def as_dict(self):
        dictionary = {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
        return dictionary

class Pipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coordinates = db.Column(db.String(500))
    def __repr__(self):
        return '<Pipe {0} {1}>'.format(self.id, self.coordinates)

class Indication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dateofvalue = db.Column(db.DateTime)
    value = db.Column(db.Float)
    device_id=db.Column(db.Integer,db.ForeignKey('device.id'),nullable=False)

    def __repr__(self):
        return '<Device {0} {1} {2}>'.format(self.device.address_raw, self.dateofvalue, self.value)

    def as_dict(self):
        dictionary = {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
        dictionary['address']=self.device.address_raw
        return dictionary

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

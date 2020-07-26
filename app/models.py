from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100),nullable=False)
    username = db.Column(db.String(100), unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True,nullable=False)
    role = db.Column(db.String(50),nullable=False)
    password_hash = db.Column(db.String(128),nullable=False)
    deleted=db.Column(db.Boolean())

    def __repr__(self):
        return '<User {}>'.format(self.fullname)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def as_dict(self):
        dictionary = {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
        return dictionary

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100),nullable=False,index=True )
    #address_clean = db.Column(db.String(100))
    coordinates = db.Column(db.String(100))
    indications=db.relationship('Indication',backref='device',lazy=True)
    label=db.Column(db.String(50))
    deleted = db.Column(db.Boolean())
    path_to_model=db.Column(db.String(100))
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'))

    def __repr__(self):
        return '<Device {}>'.format(self.address)

    def as_dict(self):
        dictionary = {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
        return dictionary

class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    coordinates = db.Column(db.String(2700),nullable=False)
    deleted = db.Column(db.Boolean())
    devices=db.relationship('Device',backref='district',lazy=True)
    def __repr__(self):
        return '<District {0} {1}>'.format(self.id, self.name)
    def as_dict(self):
        dictionary = {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
        return dictionary

class Pipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coordinates = db.Column(db.String(500),nullable=False)
    deleted = db.Column(db.Boolean())
    def __repr__(self):
        return '<Pipe {0} {1}>'.format(self.id, self.coordinates)

class Indication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dateofvalue = db.Column(db.DateTime,nullable=False)
    volume = db.Column(db.Float)
    pressure = db.Column(db.Float)
    temperature = db.Column(db.Float)
    class_of_incident_id = db.Column(db.Integer,db.ForeignKey('class_of_incident.id'))
    deleted = db.Column(db.Boolean())
    device_id=db.Column(db.Integer,db.ForeignKey('device.id'),nullable=False)
    updated_at=db.Column(db.DateTime,index=True)
    true_class = db.Column(db.Integer)


    def __repr__(self):
        return '<Device {0} {1}>'.format(self.device.address, self.dateofvalue)

    def as_dict(self):
        dictionary = {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
        dictionary['address']=self.device.address
        dictionary['coordinates'] = self.device.coordinates
        dictionary['label'] = self.device.label
        if self.incident!=None:
            dictionary['incident'] = self.incident.name
        return dictionary

class ClassOfIncident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    indications = db.relationship('Indication', backref='incident', lazy=True)
    deleted = db.Column(db.Boolean())

    def __repr__(self):
        return '<ClassOfIncident {0}>'.format(self.name)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()
class Service(db.Model):
    
    name = db.Column(db.String(50),primary_key=True, nullable=False)
    price = db.Column(db.Float, nullable=False, default=1000.0)
    desc = db.Column(db.String(2000), nullable=False)
    part= db.relationship('Partner', backref ="cat", cascade='all, delete-orphan')
class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement = True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.name'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.cname'), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('partner.name'), nullable=True)
    date_of_request = db.Column(db.DateTime, nullable=False)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.Enum('requested', 'assigned', 'closed'), default='requested', nullable=False)
    remarks = db.Column(db.String(2000), nullable=True)
    service = db.relationship('Service', backref='service_requests')
    customer = db.relationship('Customer', backref='service_requests')
    professional = db.relationship('Partner', backref='service_requests')

    
class Partner(db.Model):
    password = db.Column(db.String(40), nullable=False)
    name = db.Column(db.String(50),primary_key=True, nullable=False)
    date_of_join = db.Column(db.DateTime, nullable=False)
    desc = db.Column(db.String(2000), nullable=False)
    sname = db.Column(db.Integer, db.ForeignKey("service.name"))
    approved = db.Column(db.Boolean, default=False, nullable=False)
    
class Customer(db.Model):
    cname = db.Column(db.String(25), primary_key=True, nullable=False)
    
    password = db.Column(db.String(40), nullable=False)
    
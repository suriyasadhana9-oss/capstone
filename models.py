from datetime import datetime
from flask_login import UserMixin
from extensions import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Staff') # Admin, Staff

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_name = db.Column(db.String(100), nullable=False)
    product_details = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Active') # Active, Completed, Cancelled
    
    # Relationships
    production = db.relationship('Production', backref='order', uselist=False, cascade="all, delete-orphan")
    shipment = db.relationship('Shipment', backref='order', uselist=False, cascade="all, delete-orphan")
    invoice = db.relationship('Invoice', backref='order', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Order('{self.buyer_name}', '{self.product_details}', '{self.status}')"

class Production(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    production_status = db.Column(db.String(50), nullable=False, default='Not Started') # Not Started, In Progress, Completed

    def __repr__(self):
        return f"Production('Order {self.order_id}', '{self.production_status}')"

class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    shipment_status = db.Column(db.String(50), nullable=False, default='Pending') # Pending, Shipped, Delivered
    tracking_id = db.Column(db.String(100), nullable=True)
    shipping_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"Shipment('Order {self.order_id}', '{self.shipment_status}')"

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    generated_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Invoice('Order {self.order_id}', '{self.total_amount}')"

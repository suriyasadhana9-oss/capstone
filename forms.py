from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class OrderForm(FlaskForm):
    buyer_name = StringField('Buyer Name', validators=[DataRequired()])
    product_details = TextAreaField('Product Details', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    deadline = DateField('Delivery Deadline', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Submit Order')

class ProductionForm(FlaskForm):
    production_status = SelectField('Production Status', choices=[
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Status')

class ShipmentForm(FlaskForm):
    shipment_status = SelectField('Shipment Status', choices=[
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered')
    ], validators=[DataRequired()])
    tracking_id = StringField('Tracking ID')
    shipping_date = DateField('Shipping Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Update Shipment')

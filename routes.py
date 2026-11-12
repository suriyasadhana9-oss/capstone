from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from extensions import db, bcrypt
from models import User, Order, Production, Shipment, Invoice
from forms import LoginForm, OrderForm, ProductionForm, ShipmentForm
from datetime import datetime

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route("/dashboard")
@login_required
def dashboard():
    total_orders = Order.query.count()
    active_orders = Order.query.filter_by(status='Active').count()
    completed_orders = Order.query.filter_by(status='Completed').count()
    delayed_orders = Order.query.filter(Order.deadline < datetime.utcnow(), Order.status != 'Completed').count()
    return render_template('dashboard.html', title='Dashboard', 
                           total=total_orders, active=active_orders,
                           completed=completed_orders, delayed=delayed_orders)

@main.route("/orders")
@login_required
def orders():
    all_orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('orders.html', title='Orders', orders=all_orders)

@main.route("/order/new", methods=['GET', 'POST'])
@login_required
def new_order():
    form = OrderForm()
    if form.validate_on_submit():
        order = Order(buyer_name=form.buyer_name.data,
                      product_details=form.product_details.data,
                      quantity=form.quantity.data,
                      deadline=form.deadline.data)
        db.session.add(order)
        db.session.commit()
        
        # Initialize Production and Shipment records
        production = Production(order_id=order.id)
        shipment = Shipment(order_id=order.id)
        db.session.add(production)
        db.session.add(shipment)
        db.session.commit()
        
        flash('Order has been created successfully!', 'success')
        return redirect(url_for('main.orders'))
    return render_template('order_form.html', title='New Order', form=form, legend='Create Order')

@main.route("/order/<int:order_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderForm()
    if form.validate_on_submit():
        order.buyer_name = form.buyer_name.data
        order.product_details = form.product_details.data
        order.quantity = form.quantity.data
        order.deadline = form.deadline.data
        db.session.commit()
        flash('Order has been updated!', 'success')
        return redirect(url_for('main.orders'))
    elif request.method == 'GET':
        form.buyer_name.data = order.buyer_name
        form.product_details.data = order.product_details
        form.quantity.data = order.quantity
        form.deadline.data = order.deadline
    return render_template('order_form.html', title='Edit Order', form=form, legend='Update Order')

@main.route("/order/<int:order_id>/delete", methods=['POST'])
@login_required
def delete_order(order_id):
    if current_user.role != 'Admin':
        flash('Only Admins can delete orders.', 'danger')
        return redirect(url_for('main.orders'))
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Order has been deleted!', 'success')
    return redirect(url_for('main.orders'))

@main.route("/production", methods=['GET'])
@login_required
def production():
    orders = Order.query.filter(Order.status != 'Completed').order_by(Order.deadline.asc()).all()
    return render_template('production.html', title='Production Tracking', orders=orders)

@main.route("/production/<int:order_id>/update", methods=['GET', 'POST'])
@login_required
def update_production(order_id):
    order = Order.query.get_or_404(order_id)
    form = ProductionForm()
    if request.method == 'GET':
        form.production_status.data = order.production.production_status
    if form.validate_on_submit():
        order.production.production_status = form.production_status.data
        if form.production_status.data == 'Completed':
            order.status = 'Ready for Shipping'
        db.session.commit()
        flash('Production status updated.', 'success')
        return redirect(url_for('main.production'))
    return render_template('update_status.html', title='Update Production', form=form, order=order, type='Production')

@main.route("/shipping", methods=['GET'])
@login_required
def shipping():
    orders = Order.query.filter(Order.status.in_(['Ready for Shipping', 'Shipped'])).all()
    return render_template('shipping.html', title='Shipping Management', orders=orders)

@main.route("/shipping/<int:order_id>/update", methods=['GET', 'POST'])
@login_required
def update_shipping(order_id):
    order = Order.query.get_or_404(order_id)
    form = ShipmentForm()
    if request.method == 'GET':
        form.shipment_status.data = order.shipment.shipment_status
        form.tracking_id.data = order.shipment.tracking_id
        if order.shipment.shipping_date:
            form.shipping_date.data = order.shipment.shipping_date
    if form.validate_on_submit():
        order.shipment.shipment_status = form.shipment_status.data
        order.shipment.tracking_id = form.tracking_id.data
        if form.shipping_date.data:
            order.shipment.shipping_date = form.shipping_date.data
            
        if form.shipment_status.data == 'Delivered':
            order.status = 'Completed'
            # Also create an invoice automatically
            if not order.invoice:
                inv = Invoice(order_id=order.id, total_amount=order.quantity * 50.0) # Dummy 50 per item
                db.session.add(inv)
        elif form.shipment_status.data == 'Shipped':
            order.status = 'Shipped'
            
        db.session.commit()
        flash('Shipping details updated.', 'success')
        return redirect(url_for('main.shipping'))
    return render_template('update_status.html', title='Update Shipping', form=form, order=order, type='Shipping')

@main.route("/invoice/<int:order_id>")
@login_required
def invoice(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('invoice.html', title='Invoice', order=order)

import os
from datetime import datetime, timedelta
from app import create_app
from extensions import db, bcrypt
from models import User, Order, Production, Shipment, Invoice

app = create_app()

def reset_db():
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()

        print("Created database schema.")

        # Create Admin
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        admin = User(username='admin', password=hashed_password, role='Admin')
        
        # Create Staff
        staff_pass = bcrypt.generate_password_hash('staff123').decode('utf-8')
        staff = User(username='staff', password=staff_pass, role='Staff')
        
        db.session.add(admin)
        db.session.add(staff)
        db.session.commit()
        print("Created User accounts (admin/password123, staff/staff123).")

        # Create some Orders
        o1 = Order(buyer_name='Global Fabrics Ltd', product_details='Premium Cotton Shirts - Size L', quantity=1000, deadline=datetime.utcnow() + timedelta(days=5), status='Active')
        o2 = Order(buyer_name='Euro Denim Co.', product_details='Raw Denim Jeans 32x32', quantity=500, deadline=datetime.utcnow() + timedelta(days=2), status='Active')
        o3 = Order(buyer_name='Oriental Silks', product_details='Satin Silk Rolls (Blue & Red)', quantity=200, deadline=datetime.utcnow() - timedelta(days=1), status='Active') # Delayed
        o4 = Order(buyer_name='Atlantic Weavers', product_details='Winter Wool Sweaters', quantity=750, deadline=datetime.utcnow() - timedelta(days=10), status='Completed')
        
        db.session.add_all([o1, o2, o3, o4])
        db.session.commit()
        
        # Production for o1 (Not Started)
        p1 = Production(order_id=o1.id, production_status='Not Started')
        s1 = Shipment(order_id=o1.id, shipment_status='Pending')

        # Production for o2 (In Progress)
        p2 = Production(order_id=o2.id, production_status='In Progress')
        s2 = Shipment(order_id=o2.id, shipment_status='Pending')

        # Production for o3 (Completed, ready for shipping)
        o3.status = 'Ready for Shipping'
        p3 = Production(order_id=o3.id, production_status='Completed')
        s3 = Shipment(order_id=o3.id, shipment_status='Pending')
        
        # Production for o4 (Shipped & Delivered)
        p4 = Production(order_id=o4.id, production_status='Completed')
        s4 = Shipment(order_id=o4.id, shipment_status='Delivered', tracking_id='AWB-987654321', shipping_date=datetime.utcnow() - timedelta(days=2))
        i4 = Invoice(order_id=o4.id, total_amount=o4.quantity * 50.0, generated_date=datetime.utcnow() - timedelta(days=2))
        
        db.session.add_all([p1, s1, p2, s2, p3, s3, p4, s4, i4])
        db.session.commit()
        print("Created Sample Orders, Production, Shipping, and Invoice records.")

if __name__ == '__main__':
    reset_db()
    print("Database initialization complete.")

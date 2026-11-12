from flask import Flask
from extensions import db, bcrypt, login_manager
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'textile_export_secret_key_12345'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from datetime import datetime
    @app.context_processor
    def inject_now():
        return {'datetime': datetime}

    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        from models import Order, Production, Shipment, Invoice
        db.create_all()
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

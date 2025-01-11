from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from config import Config

db = SQLAlchemy()
admin = Admin(template_mode='bootstrap3')  # Initialize without app


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

    # Initialize extensions
    db.init_app(app)
    admin.init_app(app)

    # Import and register routes
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Import models and create Database
    from app.models import Product, User
    # Ensure the database is created
    with app.app_context():
        db.create_all()

    # add models to Flask-Admin
    admin.add_view(ModelView(Product, db.session))
    admin.add_view(ModelView(User, db.session))

    return app

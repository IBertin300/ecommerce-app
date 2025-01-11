from flask_admin.form import rules
from flask import flash
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash
from app.models.models import User
from wtforms import StringField


class UserAdmin(ModelView):
    # Display only these columns in the list view
    column_list = ['id', 'username', 'email', 'password']
    form_columns = ['username', 'email', 'password']

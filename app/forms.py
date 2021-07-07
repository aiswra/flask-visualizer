from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField,DecimalField
from database import engine
import pandas as pd

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

class GroupSelectionForm(Form):
    df = pd.read_sql_table('Dummy', engine)
    group_choices = df['group'].unique()
    group = SelectField('Group',choices=group_choices)

class AddItem(Form):
    x = DecimalField('x')
    y = DecimalField('y')
    group = StringField('Group')

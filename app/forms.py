from flask.ext.wtf import Form
from wtforms.fields import TextField, IntegerField, SelectField, FileField, PasswordField
from wtforms.validators import Required, Length, DataRequired, Email


class LoginForm(Form):
    email = TextField('Email Address', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class ProfileForm(Form):
    firstname = TextField('First Name', validators = [DataRequired()])
    lastname = TextField('Last Name', validators = [DataRequired()])
    age = IntegerField('Age', validators=[Required("Required")])
    sex = SelectField(u'Sex', choices = [('Male', 'Male'), ('Female', 'Female')])
    email = TextField('Email Address', validators=[Length(min=6, max=100), Required("Required"), Email()])
    password = PasswordField('Password', validators=[Required("Required"), Length(min=4, max=100)])
    

class WishForm(Form):
    title = TextField('Title')
    description = TextField('Description')
    description_url = TextField('Reference')
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional


class AddUserForm(FlaskForm):
    """Form for adding users."""

    first_name = StringField(validators=[DataRequired()])
    last_name = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[Length(min=6)])


class EditUserForm(FlaskForm):
    """ Form to edit user info """
    first_name = StringField(validators=[Optional()])
    last_name = StringField(validators=[Optional()])
    email = StringField(validators=[Optional(), Email()])
    password = PasswordField()
    
    
class ChangePasswordForm(FlaskForm):
    """ User can change password and keep it safe! """
    
    old_password = PasswordField()
    new_password = PasswordField(validators=[Length(min=6)])
    repeat_new_password = PasswordField(validators=[Length(min=6)])
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length


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

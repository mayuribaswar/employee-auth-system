import re

from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
)

from models import User


def _password_strength_check(form, field):
    password = field.data or ""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must include at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must include at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValidationError("Password must include at least one number.")
    if not re.search(r"[^\w\s]", password):
        raise ValidationError("Password must include at least one symbol.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class RegisterForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField(
        "Password",
        validators=[DataRequired(), _password_strength_check],
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create account")

    def validate_email(self, field):
        existing = User.query.filter_by(email=field.data.lower()).first()
        if existing:
            raise ValidationError("Email is already registered. Please sign in.")


class AdminUserCreateForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField(
        "Temporary password",
        validators=[DataRequired(), _password_strength_check],
    )
    role = SelectField(
        "Role",
        choices=[("user", "User (Employee)"), ("admin", "Admin")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Create user")

    def validate_email(self, field):
        existing = User.query.filter_by(email=field.data.lower()).first()
        if existing:
            raise ValidationError("A user with this email already exists.")


class AdminUserEditForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    role = SelectField(
        "Role",
        choices=[("user", "User (Employee)"), ("admin", "Admin")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Save changes")

    def __init__(self, user_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id

    def validate_email(self, field):
        existing = User.query.filter(User.email == field.data.lower(), User.id != self.user_id).first()
        if existing:
            raise ValidationError("Another user already uses this email.")


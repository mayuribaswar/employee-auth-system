import re

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
)

from models import Department, User


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
        choices=[("employee", "Employee"), ("manager", "Manager"), ("admin", "Admin")],
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
        choices=[("employee", "Employee"), ("manager", "Manager"), ("admin", "Admin")],
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


class ProfileUpdateForm(FlaskForm):
    profile_image = FileField(
        "Profile image",
        validators=[FileAllowed(["jpg", "jpeg", "png", "webp"], "Only JPG, PNG, or WEBP images are allowed.")],
    )
    phone = StringField("Phone", validators=[Length(max=30)])
    department_id = SelectField("Department", coerce=int, choices=[])
    designation = StringField("Designation", validators=[Length(max=120)])
    address = TextAreaField("Address", validators=[Length(max=1000)])
    submit = SubmitField("Save profile")

    def set_department_choices(self):
        departments = Department.query.order_by(Department.name.asc()).all()
        self.department_id.choices = [(0, "—")] + [(d.id, d.name) for d in departments]


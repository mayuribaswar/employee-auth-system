from datetime import date, datetime, time, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    users = db.relationship("User", back_populates="department", lazy="dynamic")


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Roles: admin | manager | employee
    role = db.Column(db.String(20), nullable=False, default="employee", index=True)

    # HR profile fields
    profile_image = db.Column(db.String(255), nullable=True)  # filename stored in static/uploads
    phone = db.Column(db.String(30), nullable=True)
    designation = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True, index=True)
    department = db.relationship("Department", back_populates="users")

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    attendances = db.relationship("Attendance", back_populates="user", cascade="all, delete-orphan")
    leaves = db.relationship("Leave", back_populates="user", cascade="all, delete-orphan")
    activity_logs = db.relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_manager(self) -> bool:
        return self.role == "manager"


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    check_in_time = db.Column(db.Time, nullable=True)
    check_out_time = db.Column(db.Time, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Present")  # Present | Absent

    user = db.relationship("User", back_populates="attendances")

    __table_args__ = (db.UniqueConstraint("user_id", "date", name="uq_attendance_user_date"),)


class Leave(db.Model):
    __tablename__ = "leaves"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    leave_type = db.Column(db.String(50), nullable=False, default="Annual")
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Pending")  # Pending | Approved | Rejected
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", back_populates="leaves")


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    user = db.relationship("User", back_populates="activity_logs")



import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")

    # For local development you can use:
    # postgresql://postgres:password@localhost/employee_db
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@localhost/employee_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cookie/session hardening (still works on http://localhost)
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SAMESITE = "Lax"

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "static/uploads")
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4MB


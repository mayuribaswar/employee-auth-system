from app import create_app
from extensions import db
from models import User


def seed_admin():
    app = create_app()
    with app.app_context():
        db.create_all()

        email = "admin@example.com"
        existing = User.query.filter_by(email=email).first()
        if existing:
            if existing.role != "admin":
                existing.role = "admin"
                db.session.commit()
            print("Admin already exists:", email)
            return

        admin = User(name="Admin", email=email, role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Seeded admin:", email, "password=admin123")


if __name__ == "__main__":
    seed_admin()


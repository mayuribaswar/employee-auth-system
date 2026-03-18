# Employee Authentication System

Modern, production-ready **Employee Authentication System** built with **Flask + PostgreSQL**, featuring secure session-based authentication, role-based access control, and a responsive SaaS-style dashboard UI.

## Features

- **Employee (User)**
  - Register (name, email, password)
  - Login / Logout
  - User dashboard + profile
- **Admin**
  - Admin-only login (no public admin registration)
  - Admin dashboard (stats cards)
  - User management panel (CRUD)
  - Search + pagination
  - Role changes (user/admin)
- **Security**
  - Password hashing (Werkzeug)
  - Session-based auth (Flask-Login)
  - CSRF protection (Flask-WTF)
  - Email validation + password strength validation

## Tech stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: PostgreSQL (`psycopg2-binary`)
- **Frontend**: Bootstrap 5, Bootstrap Icons, HTML/CSS

## Screenshots

Add screenshots here (placeholders):

- `docs/screenshots/landing.png`
- `docs/screenshots/login.png`
- `docs/screenshots/admin-users.png`

## Setup (Windows / PowerShell)

### 1) Install dependencies

```bash
cd employee_auth_system
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Database migrations

This project uses **Flask-Migrate** (Alembic) for schema updates.

First-time migration setup:

```bash
flask --app app.py db init
flask --app app.py db migrate -m "Initial HR modules"
flask --app app.py db upgrade
```

After future model changes:

```bash
flask --app app.py db migrate -m "Describe change"
flask --app app.py db upgrade
```

### 2) Set up PostgreSQL

1. Install PostgreSQL.
2. Create a database named `employee_db`.

If you have `psql` available:

```sql
CREATE DATABASE employee_db;
```

### 3) Configure the database URL

Set your connection string in `config.py` or via environment variable `DATABASE_URL`.

Example:

```text
postgresql://postgres:root@localhost/employee_db
```

### 4) Seed the default admin

Creates the default admin user:

- Email: `admin@example.com`
- Password: `admin123`

```bash
python seed.py
```

### 5) Run the app

```bash
python app.py
```

Open `http://127.0.0.1:5000/`.

## Routes

- **Public**: `/`, `/login`, `/register`, `/logout`
- **User**: `/user/dashboard`, `/user/profile`
- **Admin**: `/admin/dashboard`, `/admin/users`, `/admin/add-user`, `/admin/edit-user/<id>`, `/admin/delete-user/<id>` (POST)

## Folder structure

```text
employee_auth_system/
├── app.py
├── config.py
├── create_db.py
├── extensions.py
├── forms.py
├── models.py
├── requirements.txt
├── seed.py
├── static/
│   └── css/
│       └── styles.css
├── templates/
│   ├── admin/
│   ├── auth/
│   ├── errors/
│   ├── layout/
│   └── user/
└── instance/
```

## Notes

- Never commit secrets. Use environment variables (e.g. `DATABASE_URL`, `SECRET_KEY`) or a local `.env` file (kept out of Git via `.gitignore`).



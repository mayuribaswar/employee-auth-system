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

ocal `.env` file (kept out of Git via `.gitignore`).



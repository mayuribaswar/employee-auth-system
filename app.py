import os
import uuid
from functools import wraps

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from config import Config
from extensions import csrf, db, login_manager, migrate
from forms import (
    AdminUserCreateForm,
    AdminUserEditForm,
    LoginForm,
    ProfileUpdateForm,
    RegisterForm,
)
from models import ActivityLog, Department, User


def log_activity(action: str, user: User | None = None):
    db.session.add(ActivityLog(user_id=getattr(user, "id", None), action=action))
    db.session.commit()


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("auth_login", next=request.path))
        if not getattr(current_user, "is_admin", False):
            flash("You are not authorized to access that page.", "danger")
            return redirect(url_for("user_dashboard"))
        return view(*args, **kwargs)

    return wrapper


def role_required(*roles: str):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please sign in to continue.", "warning")
                return redirect(url_for("auth_login", next=request.path))
            if current_user.role not in roles:
                flash("You are not authorized to access that page.", "danger")
                return redirect(url_for("user_dashboard"))
            return view(*args, **kwargs)

        return wrapper

    return decorator


def _allowed_image(filename: str) -> bool:
    ext = (filename.rsplit(".", 1)[-1] if "." in filename else "").lower()
    return ext in {"jpg", "jpeg", "png", "webp"}


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth_login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    @app.get("/")
    def landing():
        return render_template("auth/index.html")

    @app.route("/login", methods=["GET", "POST"])
    def auth_login():
        if current_user.is_authenticated:
            return _redirect_after_login()

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.lower()).first()
            if not user or not user.check_password(form.password.data):
                flash("Invalid email or password.", "danger")
                return render_template("auth/login.html", form=form)

            login_user(user, remember=True)
            log_activity("login", user=user)
            flash("Welcome back!", "success")

            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return _redirect_after_login()

        return render_template("auth/login.html", form=form)

    @app.route("/register", methods=["GET", "POST"])
    def auth_register():
        if current_user.is_authenticated:
            return _redirect_after_login()

        form = RegisterForm()
        if form.validate_on_submit():
            user = User(
                name=form.name.data.strip(),
                email=form.email.data.lower().strip(),
                role="employee",
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()

            flash("Account created. Please sign in.", "success")
            return redirect(url_for("auth_login"))

        return render_template("auth/register.html", form=form)

    @app.get("/logout")
    @login_required
    def auth_logout():
        log_activity("logout", user=current_user)
        logout_user()
        flash("You’ve been signed out.", "info")
        return redirect(url_for("landing"))

    @app.get("/user/dashboard")
    @login_required
    def user_dashboard():
        if current_user.is_admin:
            return redirect(url_for("admin_dashboard"))
        return render_template("user/dashboard.html")

    @app.get("/user/profile")
    @login_required
    def user_profile():
        if current_user.is_admin:
            return redirect(url_for("admin_dashboard"))
        form = ProfileUpdateForm(obj=current_user)
        form.set_department_choices()
        form.department_id.data = current_user.department_id or 0
        return render_template("user/profile.html", form=form)

    @app.post("/user/profile")
    @login_required
    def user_profile_update():
        if current_user.is_admin:
            return redirect(url_for("admin_dashboard"))

        form = ProfileUpdateForm()
        form.set_department_choices()
        if not form.validate_on_submit():
            return render_template("user/profile.html", form=form), 400

        current_user.phone = (form.phone.data or "").strip() or None
        current_user.designation = (form.designation.data or "").strip() or None
        current_user.address = (form.address.data or "").strip() or None
        current_user.department_id = form.department_id.data or None

        if form.profile_image.data:
            file = form.profile_image.data
            filename = secure_filename(file.filename or "")
            if not filename or not _allowed_image(filename):
                flash("Invalid file type. Upload a JPG/PNG/WEBP image.", "danger")
                return redirect(url_for("user_profile"))

            ext = filename.rsplit(".", 1)[-1].lower()
            new_name = f"user_{current_user.id}_{uuid.uuid4().hex}.{ext}"
            upload_dir = os.path.join(app.root_path, app.config["UPLOAD_FOLDER"])
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, new_name))
            current_user.profile_image = new_name

        db.session.commit()
        log_activity("profile_updated", user=current_user)
        flash("Profile updated.", "success")
        return redirect(url_for("user_profile"))

    @app.get("/admin/dashboard")
    @role_required("admin")
    def admin_dashboard():
        total_users = User.query.count()
        total_admins = User.query.filter_by(role="admin").count()
        return render_template(
            "admin/dashboard.html",
            total_users=total_users,
            total_admins=total_admins,
        )

    @app.get("/admin/users")
    @role_required("admin")
    def admin_users():
        q = (request.args.get("q") or "").strip()
        page = int(request.args.get("page") or 1)
        per_page = 10

        query = User.query
        if q:
            like = f"%{q}%"
            query = query.filter((User.name.ilike(like)) | (User.email.ilike(like)))

        query = query.order_by(User.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return render_template(
            "admin/users.html",
            users=pagination.items,
            pagination=pagination,
            q=q,
        )

    @app.route("/admin/add-user", methods=["GET", "POST"])
    @role_required("admin")
    def admin_add_user():
        form = AdminUserCreateForm()
        if form.validate_on_submit():
            user = User(
                name=form.name.data.strip(),
                email=form.email.data.lower().strip(),
                role=form.role.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("User created.", "success")
            return redirect(url_for("admin_users"))
        return render_template("admin/add_user.html", form=form)

    @app.route("/admin/edit-user/<int:user_id>", methods=["GET", "POST"])
    @role_required("admin")
    def admin_edit_user(user_id: int):
        user = User.query.get_or_404(user_id)
        form = AdminUserEditForm(user_id=user_id, obj=user)
        if form.validate_on_submit():
            user.name = form.name.data.strip()
            user.email = form.email.data.lower().strip()
            user.role = form.role.data
            db.session.commit()
            flash("User updated.", "success")
            return redirect(url_for("admin_users"))
        return render_template("admin/edit_user.html", form=form, user=user)

    @app.post("/admin/delete-user/<int:user_id>")
    @role_required("admin")
    def admin_delete_user(user_id: int):
        user = User.query.get_or_404(user_id)
        if user.id == current_user.id:
            flash("You can’t delete your own admin account.", "danger")
            return redirect(url_for("admin_users"))
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.", "info")
        return redirect(url_for("admin_users"))

    @app.errorhandler(404)
    def not_found(_):
        return render_template("errors/404.html"), 404

    return app


def _redirect_after_login():
    if getattr(current_user, "is_admin", False):
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("user_dashboard"))


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)


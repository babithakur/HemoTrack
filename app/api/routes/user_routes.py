from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.service.user_service import UserService
from app.utils.auth import login_required

user_bp = Blueprint("user", __name__)

@user_bp.route("/")
def index():
    return render_template("index.html")

@user_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", name=session.get("name"))

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.form
    try:
        user = UserService.register_user(
            email=data.get("email"),
            password=data.get("password"),
            confirm_password=data.get("confirm_password"),
            name=data.get("name"),
            gender=data.get("gender"),
            dob=data.get("dob")
        )
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("user.index"))
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("user.index"))


@user_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    remember_me = True if request.form.get("rememberMe") else False
    try:
        UserService.login_user(email, password, remember_me)
        flash("Logged in successfully!", "success")
        return redirect(url_for("user.dashboard"))
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("user.index"))

@user_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("user.index"))




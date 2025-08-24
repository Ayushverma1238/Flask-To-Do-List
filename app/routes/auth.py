from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Login Successful!", 'success')
            return redirect(url_for('tasks.view_tasks'))
        else:
            flash("Invalid Username or Password", "danger")

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully", 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        phoneNo = request.form.get("phoneNo") # Keep as string
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_pass = request.form.get("confirm_password")

        # --- Input Validation ---
        if not all([name, phoneNo, email, username, password, confirm_pass]):
            flash("Please fill out all fields.", "danger")
            return redirect(url_for("auth.register"))

        # --- Check for existing username and email ---
        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(username=username).first():
            flash("Username already taken. Please choose another one.", "danger")
            return redirect(url_for("auth.register"))
        
        if password != confirm_pass:
            flash("Passwords did not match.", 'danger')
            return redirect(url_for("auth.register"))
    
        hashed_pass = generate_password_hash(password, method="pbkdf2:sha256")
        
        # Use the original phoneNo string
        newUser = User(name=name, username=username, password=hashed_pass, phoneNo=phoneNo, email=email)
        
        db.session.add(newUser)
        db.session.commit()

        flash("Register succefully. Please login.", 'success')
        return redirect(url_for("auth.login"))
    return render_template("register.html")

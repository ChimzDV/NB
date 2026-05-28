from flask import Blueprint, render_template, request, redirect
from app import db
from app.models.user import User
from flask_login import login_user
from werkzeug.security import check_password_hash
from flask_login import logout_user

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("auth/register.html")

    existing_user = User.query.filter_by(
        email=request.form["email"]
    ).first()

    if existing_user:
        return "Email already exists"

    user = User(
        full_name=request.form["full_name"],
        email=request.form["email"],
        phone=request.form["phone"],
        national_id=request.form["national_id"]
    )

    user.set_password(request.form["password"])

    db.session.add(user)
    db.session.commit()

    print("Registration Successful")
    return render_template("auth/login.html")

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("auth/login.html")

    user = User.query.filter_by(
        email=request.form["email"]
    ).first()

    if not user:
        return "User not found"

    if not user.check_password(request.form["password"]):
        return "Invalid password"

    login_user(user)

    return redirect("/dashboard")    

@auth.route("/logout")
def logout():

    logout_user()

    print("Logged Out Successfully")
    return render_template("auth/login.html")    
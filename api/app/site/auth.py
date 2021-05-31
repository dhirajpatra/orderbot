import functools
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
import hashlib

from . import site
from . import auth
from ..models import User, Message, User_api_details, db
from ..forms import NameForm



def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("site.login"))

        return view(**kwargs)

    return wrapped_view


@auth.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            User.query.filter_by(id = user_id).first()
        )


@auth.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        password = request.form["password"]
        password_confirm = request.form["password_confirm"]
        phone_number = request.form['phone_number']
        phone_number_encrypted = hashlib.md5(phone_number.encode()).hexdigest()
        email = request.form['email']

        error = None

        if not password:
            error = "Password is required."
        elif not phone_number:
            error = "Phone Number is required."
        elif password != password_confirm:
            error = "Password and confirm password mismatch"
        elif (
            User.query.filter_by(phone_number = phone_number).count() > 0
        ):
            error = f"User {phone_number} is already registered."

        if error is None:
            # hashing the password
            password_hash = generate_password_hash(password)
            # the name is available, store it in the database and go to
            # the login page
            new_user = User(phone_number=phone_number, phone_number_encrypted=phone_number_encrypted, email=email, password=password_hash, type_of_business=1, welcome_msg="Hi welcome to HOLIDAY HOMES AND VILLAS IN MARINA DI NOTO, SICILY.\nRelevant Accommodations\nDiscover our accommodations in Marina di Noto (Syracuse), near the sea\n\nHow can I help you?", hook="")
            db.session.add(new_user)
            db.session.commit()

            new_user_api_details = User_api_details(user_id=new_user.id)
            db.session.add(new_user_api_details)
            db.session.commit()

            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("site/register.html")


@auth.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    error = None
    if request.method == "POST":
        phone_number = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(phone_number=phone_number).first()

        if user is None:
            error = "Incorrect username. It should be your phone number with country code. eg. 441234567890"
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."
        
        if error is None:
            
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("site.index"))

        return render_template('site/login.html', error=error)
    return render_template('site/login.html', error=error)


@auth.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect("/login")

from flask import Flask, render_template, redirect, flash, session, g, request, jsonify, sessions
# from general.secrets import secret_password
from general.models import db, connect_db, User
from general.forms import LoginForm, AddUserForm
from sqlalchemy.exc import IntegrityError
import os


CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ECHO"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
connect_db(app)

import routes.user_routes
import routes.product_routes


@app.errorhandler(404)
def not_found(error):
    """ Handles 404 errors """
    return render_template("errors/404.html")


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get_or_404(session[CURR_USER_KEY])

    else:
        g.user = None


def login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route("/")
def show_index():
    """ Shows index template. """
    return redirect("/products")


@app.route("/signup", methods=["POST", "GET"])
def show_signup():
    """
    Signs user up if form is submitted.
    Redirects back to signup if error is made.
    """
    if g.user:
        return redirect("/products")

    form = AddUserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name=form.first_name.data.title(),
                last_name=form.last_name.data.title(),
                email=form.email.data.lower(),
                password=form.password.data,
            )

            db.session.commit()

        except IntegrityError:
            flash(
                "The e-mail address you entered is already in use. Please log in or try another e-mail address.", "danger")
            return render_template("forms/signup.html", form=form)

        login(user)
        return redirect(f"/products")

    else:
        return render_template("forms/signup.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def show_login():

    if g.user:
        return redirect("/products")

    form = LoginForm()

    if form.validate_on_submit():

        user = User.authenticate(form.email.data, form.password.data)

        if user:
            login(user)

            flash(f"Hello, {user.first_name}!", "success")

            return redirect("/products")

        flash("Invalid credentials.", 'danger')
        return redirect("/login")

    else:
        return render_template("forms/login.html", form=form)


@app.route("/logout")
def logout():

    if not g.user:
        return redirect("/")

    do_logout()
    user = User.query.get_or_404(g.user.id)
    flash(f"Goodbye {user.first_name}!", "warning")
    return redirect("/")


@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req

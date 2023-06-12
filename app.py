import requests
from secrets import secret_password, stripe_key
from forms import AddUserForm, LoginForm, EditUserForm, ChangePasswordForm
from models import db, connect_db, ProductModel, User, deslugify
from sqlalchemy.exc import IntegrityError
from flask import Flask, render_template, redirect, flash, session, g, request, jsonify, sessions
import stripe


CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///capstone1-stripe"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

app.config["SECRET_KEY"] = secret_password

stripe.api_key = stripe_key

connect_db(app)

categories = ProductModel.get_categories()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.errorhandler(404)
def not_found(error):
    """ Handles 404 errors """
    return render_template("errors/404.html")


@app.errorhandler(500)
def server_error(error):
    """ Handles 500 errors """
    return render_template("500.html")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.route("/")
def show_index():
    """ Shows index template. """
    return redirect("/products")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.route("/logout")
def logout():

    if not g.user:
        return redirect("/")

    do_logout()
    user = User.query.get_or_404(g.user.id)
    flash(f"Goodbye {user.first_name}!", "warning")
    return redirect("/")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

MAX_ITEMS_PER_PAGE = 6

# General routes for app
@app.route("/products")
def show_all_products():

    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)

    if not search:
        products = ProductModel.query.paginate(page=page, per_page=MAX_ITEMS_PER_PAGE)
    else:
        products = ProductModel.query.filter(
            ProductModel.title.ilike(f"%{search}%") |
            ProductModel.category.ilike(f"%{search}%")
        ).paginate(page=page, per_page=8)

    return render_template("products/list-products.html", products=products, categories=categories, search=search)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.route("/products/<id>")
def show_product(id):
    """ Shows a product """
    product = ProductModel.query.get_or_404(id)

    similar_products = ProductModel.query.filter(
        ProductModel.category.ilike(f"%{product.category}%")).all()

    return render_template("products/product.html", product=product, similar_products=similar_products, categories=categories)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.route("/products/categories/<category>")
def show_products_by_category(category):
    """ Shows list of products by category """

    page = request.args.get('page', 1, type=int)

    category = deslugify(category)
    products = ProductModel.query.filter(
        ProductModel.category == category).paginate(page=page, per_page=MAX_ITEMS_PER_PAGE)
    categories = ProductModel.get_categories()

    return render_template("products/list-products.html", products=products, category=category, categories=categories)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.route("/my-account")
def show_account():
    """ Shows the account of the logged in user. If not logged in, redirects to home """
    if g.user:
        user = User.query.get_or_404(g.user.id)
        return render_template("account.html", user=user)
    else:
        return redirect("/login")


@app.route("/my-account/edit", methods=["GET", "POST"])
def edit_account():
    """Update profile for current user."""

    if not g.user:
        flash("Please log in to make changes to your account.", "danger")
        return redirect("/login")

    form = EditUserForm()
    user = User.query.get_or_404(g.user.id)

    if form.validate_on_submit():
        if user.authenticate(user.email, form.password.data):
            # User is authenticated, update info
            user.first_name = form.first_name.data.title() or user.first_name
            user.last_name = form.last_name.data.title() or user.last_name
            user.email = form.email.data.lower() or user.email

        else:
            # User is not authenticated, kick them back to the form
            flash("Entered incorrect password", "danger")
            return render_template("/forms/edit-user.html", form=form)
        try:
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash(
                "The e-mail address you entered is already in use, please try another.", "danger")
            return render_template("forms/edit-user.html", form=form)

        flash("Your account has been updated.", "success")
        return redirect(f"/my-account")

    return render_template("/forms/edit-user.html", form=form)


@app.route("/my-account/change-password", methods=["GET", "POST"])
def user_change_password():
    """ Logged in user can change their password here """
    if not g.user:
        flash("Please log in.", "danger")
        return redirect("/login")

    form = ChangePasswordForm()
    user = User.query.get_or_404(g.user.id)

    if form.validate_on_submit():
        if user.authenticate(user.email, form.old_password.data):
            # User is authenticated, attempt to update info
            password = form.new_password.data
            repeat = form.repeat_new_password.data

            if password != repeat:
                flash("Passwords did not match", "danger")
                return render_template("/forms/change-password.html", form=form)

            user.change_password(user.email, password)

            db.session.add(user)
            db.session.commit()

            flash("Your account has been updated.", "success")
            return redirect(f"/my-account")

        # User is not authenticated, kick them back to the form
        flash("Entered incorrect password", "danger")
        return render_template("/forms/change-password.html", form=form)

    return render_template("/forms/change-password.html", form=form)


@app.route("/cart", methods=["GET", "POST", "PATCH"])
def cart():
    """
    GET: Show currently logged-in users cart as a list of products
    POST: Add product to cart of currently logged-in user
    PATCH: Increment or Decrement the quantity of an item in the cart
    """

    if not g.user:
        data = {
            "message": "Please log in to interact with your shopping cart",
            "class": "danger"
        }
        return jsonify({"data": data})

    else:
        user = User.query.get_or_404(g.user.id)

        if request.method == "GET":
            cart = user.cart
            return render_template("cart.html", user=user, cart=cart)

        prod_id = request.get_json()["id"]
        product = ProductModel.query.get_or_404(prod_id)

        if request.method == "POST":
            session[f"qty_{prod_id}"] = 1

            user.cart.append(product)
            db.session.commit()

            data = {
                "message": f"Added {product.title} to cart.",
                "method": f"{request.method}",
                "qty": session.get(f"qty_{prod_id}")
            }

        elif request.method == "PATCH":

            if request.get_json()["role"] == "increment":
                session[f"qty_{prod_id}"] += 1
            else:
                session[f"qty_{prod_id}"] -= 1

            data = {
                "message": f"Added {product.title} to cart.",
                "method": f"{request.method}",
                "qty": session.get(f"qty_{prod_id}")
            }

        return jsonify({"data": data})


@app.route("/cart/delete", methods=["DELETE"])
def remove_from_cart():
    if not g.user:
        flash("Please log in to interact with your shopping cart", "danger")
        return redirect("/login")

    user = User.query.get_or_404(g.user.id)

    prod_id = request.get_json()["id"]
    product = ProductModel.query.get_or_404(prod_id)

    user.cart.remove(product)
    db.session.commit()

    data = {
        "message": f"Removed {product.title} from cart.",
        "method": f"{request.method}"
    }

    return jsonify({"data": data})


@app.route("/favorites", methods=["GET", "POST"])
def show_favorites():
    """ shows user their favorites if logged in """

    if not g.user:
        data = {
            "message": "Please log in to interact with your favorites list",
            "class": "danger"
        }
        return jsonify({"data": data})

    user = User.query.get_or_404(g.user.id)

    if request.method == "POST":
        prod_id = request.get_json()["id"]
        product = ProductModel.query.get_or_404(prod_id)

        user.favorites.append(product)
        db.session.commit()

        data = {
            "message": f"Added {product.title} to favorites.",
            "method": f"{request.method}"
        }

        return jsonify({"data": data})

    elif request.method == "GET":
        favorites = user.favorites
        return render_template("favorites.html", favorites=favorites)

    else:
        return render_template("invalid-method.html")


@app.route("/favorites/delete", methods=["DELETE"])
def delete_favorite():
    """ deletes a favorite from user.favorites in the db """

    if not g.user:
        flash("Please log in to interact with your favorites")
        return redirect("/login")

    if request.method != "DELETE":
        return render_template("invalid-method.html")

    user = User.query.get_or_404(g.user.id)

    prod_id = request.get_json()["id"]
    product = ProductModel.query.get_or_404(prod_id)

    user.favorites.remove(product)
    db.session.commit()

    data = {
        "message": f"Removed {product.title} from favorites.",
        "method": f"{request.method}"
    }

    return jsonify({"data": data})


# TODO : Checkout


@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req

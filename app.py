"""
Capstone project!

# TODO: Project proposal revision
# TODO: Setup Heroku and deploy
"""
import requests
from secrets import secret_password
from forms import AddUserForm, LoginForm, EditUserForm
from models import db, connect_db, Product, User
from sqlalchemy.exc import IntegrityError
from flask import Flask, render_template, redirect, flash, session, g, request, jsonify


CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///capstone1"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = secret_password

connect_db(app)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Error Routes: not found, server error, client errors
# TODO : Error routes
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
        g.user = User.query.get(session[CURR_USER_KEY])

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
    user = User.query.get(g.user.id)
    flash(f"Goodbye {user.first_name}!", "warning")
    return redirect("/")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# General routes for app
@app.route("/products")
def show_all_products():

    products = Product.query.all()

    return render_template("products/list-products.html", products=products)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.route("/products/<int:id>")
def show_product(id):
    """ Shows a product """
    product = Product.query.get(id)

    similar_products = Product.query.filter(
        Product.category.ilike(f"%{product.category}%")).all()

    return render_template("products/product.html", product=product, similar_products=similar_products)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.route("/products/<category>")
def show_products_by_category(category):
    """ Shows list of products by category """

    products = Product.query.filter(Product.category == category).all()

    return render_template("products/list-products.html", products=products, category=category)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.route("/my-account")
def show_account():
    """ Shows the account of the logged in user. If not logged in, redirects to home """
    if g.user:
        user = User.query.get(g.user.id)
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
            user.last_name=form.last_name.data.title() or user.last_name
            user.email=form.email.data.lower() or user.email
                        
        else:
            # User is not authenticated, kick them back to the form
            flash("Entered incorrect password", "danger")
            return render_template("/forms/edit-user.html", form=form)
        try:
            db.session.add(user)
            db.session.commit()
                
        except IntegrityError:
            db.session.rollback()
            flash("The e-mail address you entered is already in use, please try another.", "danger")
            return render_template("forms/edit-user.html", form=form)
        
        flash("Your account has been updated.", "success")
        return redirect(f"/my-account")
    
    return render_template("/forms/edit-user.html", form=form)
        

@app.route("/cart", methods=["GET", "POST"])
def cart():
    """ 
    GET: Show currently logged-in users cart as a list of products
    POST: Add product to cart of currently logged-in user
    """

    if not g.user:
        flash("Please log in to interact with your shopping cart", "danger")
        return redirect("/login")

    else:
        user = User.query.get(g.user.id)
        
        if request.method == "POST":
            prod_id = int(request.get_json()["id"])
            product = Product.query.get_or_404(prod_id)
            
            user.cart.append(product)
            db.session.commit()
            
            data = {
                "message": f"Added {product.title} to cart.",
                "method": f"{request.method}"
            }
            
            return jsonify({"response": data})
        else:
            cart = user.cart
            return render_template("cart.html", user=user, cart=cart)
        

@app.route("/cart/delete", methods=["DELETE"])
def remove_from_cart():
    if not g.user:
        flash("Please log in to interact with your shopping cart", "danger")
        return redirect("/login")
    
    user = User.query.get_or_404(g.user.id)
    
    prod_id = int(request.get_json()["id"])
    product = Product.query.get_or_404(prod_id)
    
    user.cart.remove(product)
    db.session.commit()
    
    data = {
        "message": f"Removed {product.title} from cart.",
        "method": f"{request.method}"
    }
    
    return jsonify({"response": data})
# TODO : add to favorites
# TODO : remove from favorites

# TODO : Checkout
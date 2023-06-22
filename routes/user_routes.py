from flask import render_template, redirect, flash, session, g, request, jsonify
from sqlalchemy.exc import IntegrityError
from general.forms import EditUserForm, ChangePasswordForm
from general.models import Product, User, Cart
from app import app, db

from general.secrets import stripe_key
import stripe
stripe.api_key = stripe_key

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

        return jsonify(data)

    user = User.query.get_or_404(g.user.id)

    if request.method == "GET":
        # query = db.session.query(Product, Cart).join(Cart, Product.id == Cart.prod_id).all()
        products = Product.query.join(
            Cart, Product.id == Cart.prod_id).filter(Cart.user_id == g.user.id)

        sub_total = user.get_subtotal()

        return render_template("cart.html", user=user, products=products, total=sub_total)

    if request.method == "POST":
        prod_id = request.get_json()["id"]
        product = Product.query.get(prod_id)
        new_cart_instance = Cart(user_id=user.id, prod_id=prod_id)
        db.session.add(new_cart_instance)

        try:
            db.session.commit()
            user.num_items_in_cart += 1
            data = {
                "message": "Created new cart instance",
                "instance": f"{new_cart_instance}",
                "prod_title": product.title,
                "prod_price": product.price,
                "prod_id": prod_id,
                "num_items_in_cart": user.get_num_items_in_cart()
            }

        except Exception as err:
            db.session.rollback()
            data = {
                "message": f"Failed to create new instance",
                "error": f"{type(err)}"
            }

        return jsonify(data)

    elif request.method == "PATCH":
        prod_id = request.get_json()["id"]
        role = request.get_json()["role"]

        cart_instance = Cart.get_instance(g.user.id, prod_id)
        product = Product.query.get(prod_id)

        if role == "increment":
            cart_instance.quantity += 1

        elif role == "decrement":
            cart_instance.quantity -= 1

        db.session.add(cart_instance)
        db.session.commit()

        data = {
            "cart_instance": f"{cart_instance}",
            "method": f"{request.method}",
            "message": f"{role} {product.title}.",
            "prod_price": product.price,
            "prod_id": prod_id,
            "qty": cart_instance.quantity,
            "prod_title": product.title,
            "num_items_in_cart": user.get_num_items_in_cart()
        }

        return jsonify(data)


@app.route("/cart/delete", methods=["DELETE"])
def remove_from_cart():
    if not g.user:
        flash("Please log in to interact with your shopping cart", "danger")
        return redirect("/login")

    prod_id = request.get_json()["id"]
    cart_instance = Cart.query.filter(Cart.prod_id == prod_id, Cart.user_id == g.user.id).one()

    try:
        g.user.num_items_in_cart -= cart_instance.quantity
    except:
        return jsonify({
            "message": "Something went wrong when querying Cart",
            "query_response": cart_instance
        })

    try:
        db.session.delete(cart_instance)
        db.session.commit()

    except:
        db.session.rollback()
        data = {"message": f"Failed to delete."}

    data = {
        "message": f"Deleted {cart_instance}.",
        "sub_total": g.user.get_subtotal()
    }

    return jsonify(data)


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
        product = Product.query.get_or_404(prod_id)

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
    product = Product.query.get_or_404(prod_id)

    user.favorites.remove(product)
    db.session.commit()

    data = {
        "message": f"Removed {product.title} from favorites.",
        "method": f"{request.method}"
    }

    return jsonify({"data": data})


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    session = stripe.checkout.Session.create(
        line_items=g.user.get_line_items(),
        mode='payment',
        success_url='http://localhost:5000/success',
        cancel_url='http://localhost:5000/products',
    )

    return redirect(session.url, code=303)


@app.route("/success")
def show_success_page():
    """ Shows a success page when a user purchases a product """
    g.user.made_purchase()
    return render_template("success.html")

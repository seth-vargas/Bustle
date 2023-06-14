from flask import Flask, render_template, redirect, flash, session, g, request, jsonify, sessions
from sqlalchemy.exc import IntegrityError
from general.forms import EditUserForm, ChangePasswordForm
from general.models import Product, User
from app import app, db


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
        product = Product.query.get_or_404(prod_id)

        if request.method == "POST":
            session[f"qty_{prod_id}"] = 1
            user.num_items_in_cart += 1

            db.session.add(user)
            user.cart.append(product)

        elif request.method == "PATCH":
            if request.get_json()["role"] == "increment":
                session[f"qty_{prod_id}"] += 1
                user.num_items_in_cart += 1

            else:
                session[f"qty_{prod_id}"] -= 1
                user.num_items_in_cart -= 1

        db.session.add(user)
        db.session.commit()

        data = {
            "message": f"Added {product.title} to cart.",
            "method": f"{request.method}",
            "qty": session.get(f"qty_{prod_id}"),
            "count_products_in_cart": user.num_items_in_cart
        }

        return jsonify({"data": data})


@app.route("/cart/delete", methods=["DELETE"])
def remove_from_cart():
    if not g.user:
        flash("Please log in to interact with your shopping cart", "danger")
        return redirect("/login")

    user = User.query.get_or_404(g.user.id)

    prod_id = request.get_json()["id"]
    product = Product.query.get_or_404(prod_id)

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

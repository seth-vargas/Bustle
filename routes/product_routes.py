from flask import render_template, g, request
from general.models import Product, User, Cart, deslugify, get_categories
from app import app, db


MAX_ITEMS_PER_PAGE = 6
dropdown_options = ["A-Z", "Z-A", "High-Low", "Low-High"]

# General routes for app
@app.route("/products")
def show_all_products():

    search = request.args.get("search")
    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort_by")
    cart = []

    query = Product.query

    ordered_query = order_query(query, sort_by)

    if g.user:
        cart = g.user.get_cart()

    if not search:
        products = ordered_query.paginate(
            page=page, per_page=MAX_ITEMS_PER_PAGE)
    else:
        products = ordered_query.filter(
            Product.title.ilike(f"%{search}%") |
            Product.category.ilike(f"%{search}%")
        ).paginate(page=page, per_page=MAX_ITEMS_PER_PAGE)

    return render_template("products/list-products.html", products=products, categories=get_categories(), search=search, query=cart, sort_by=sort_by, dropdown_options=dropdown_options)


@app.route("/products/<id>")
def show_product(id):
    """ Shows a product """
    product = Product.query.get_or_404(id)

    similar_products = Product.query.filter(
        Product.category.ilike(f"%{product.category}%")).all()

    return render_template("products/product.html", product=product, similar_products=similar_products, categories=get_categories())


@app.route("/products/categories/<category>")
def show_products_by_category(category):
    """ Shows list of products by category """

    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort_by")

    if g.user:
        cart = g.user.get_cart()
    else:
        cart = []

    query = Product.query.filter(Product.category == deslugify(category))

    ordered_query = order_query(query, sort_by)

    category = deslugify(category)
    products = ordered_query.paginate(page=page, per_page=MAX_ITEMS_PER_PAGE)

    return render_template("products/list-products.html", products=products, category=category, categories=get_categories(), query=cart, sort_by=sort_by, dropdown_options=dropdown_options)


def order_query(query, sort_by):
    """ Sorts a query by whatever parameters specified by user """

    if sort_by == "A-Z":
        query = query.order_by(Product.title)

    elif sort_by == "Z-A":
        query = query.order_by(Product.title.desc())

    elif sort_by == "Low-High":
        query = query.order_by(Product.price)

    elif sort_by == "High-Low":
        query = query.order_by(Product.price.desc())

    else:
        query = query.order_by(Product.id)

    return query
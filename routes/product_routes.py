from flask import render_template, g, request
from general.models import Product, User, Cart, deslugify, get_categories, get_query
from app import app, db


MAX_ITEMS_PER_PAGE = 6
dropdown_options = ["A-Z", "Z-A", "High-Low", "Low-High"]

# General routes for app
@app.route("/products")
def show_all_products():

    search = request.args.get("search")
    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort_by")
    ordered_query = db.session.query(Product, Cart).outerjoin(Cart, Cart.prod_id == Product.id).order_by(Product.id)

    if g.user:
        query = g.user.get_cart()
    else:
        query = []

    ordered_query = get_query(sort_by)

    if not search:
        products = ordered_query.paginate(
            page=page, per_page=MAX_ITEMS_PER_PAGE)
    else:
        products = ordered_query.filter(
            Product.title.ilike(f"%{search}%") |
            Product.category.ilike(f"%{search}%")
        ).paginate(page=page, per_page=MAX_ITEMS_PER_PAGE)

    return render_template("products/list-products.html", products=products, categories=get_categories(), search=search, query=query, sort_by=sort_by, dropdown_options=dropdown_options)


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
        query = g.user.get_cart()
    else:
        query = []

    ordered_query = get_query(sort_by, category)

    category = deslugify(category)
    products = ordered_query.paginate(page=page, per_page=MAX_ITEMS_PER_PAGE)

    return render_template("products/list-products.html", products=products, category=category, categories=get_categories(), query=query, sort_by=sort_by, dropdown_options=dropdown_options)

from flask import render_template, g, request
from general.models import Product, Cart, deslugify, get_categories
from app import app


MAX_ITEMS_PER_PAGE = 6

# General routes for app
@app.route("/products")
def show_all_products():

    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    # cart = Cart.query.filter(Cart.user_id == g.user.id).all()
    items_in_cart = Cart.query.filter(Cart.user_id == g.user.id).all()
    cart = []
    for item in items_in_cart:
        cart.append(Product.query.get(item.prod_id))

    if not search:
        products = Product.query.paginate(
            page=page, per_page=MAX_ITEMS_PER_PAGE)
    else:
        products = Product.query.filter(
            Product.title.ilike(f"%{search}%") |
            Product.category.ilike(f"%{search}%")
        ).paginate(page=page, per_page=MAX_ITEMS_PER_PAGE)

    return render_template("products/list-products.html", products=products, categories=get_categories(), search=search, cart=cart)


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

    page = request.args.get('page', 1, type=int)

    category = deslugify(category)
    products = Product.query.filter(
        Product.category == category).paginate(page=page, per_page=MAX_ITEMS_PER_PAGE)

    return render_template("products/list-products.html", products=products, category=category, categories=get_categories())


from flask import render_template, g, request
from general.models import Product, User, Cart, deslugify, get_categories
from app import app, db


MAX_ITEMS_PER_PAGE = 6

# General routes for app
@app.route("/products")
def show_all_products():

    search = request.args.get("search")
    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort_by")
    query = []

    if g.user:
        query = db.session.query(Product, Cart).join(
            Cart, Product.id == Cart.prod_id).all()

    product_query = db.session.query(Product, Cart).outerjoin(Cart, Cart.prod_id == Product.id).order_by(Product.title)

    if sort_by == "A-Z":
        # order by prod.title
        product_query = db.session.query(Product, Cart).outerjoin(Cart, Cart.prod_id == Product.id).order_by(Product.title)

    elif sort_by == "Z-A":
        # order by prod.title desc
        product_query = db.session.query(Product, Cart).outerjoin(Cart, Cart.prod_id == Product.id).order_by(Product.title.desc())
    
    elif sort_by == "L-H":
        # order by prod.price
        product_query = db.session.query(Product, Cart).outerjoin(Cart, Cart.prod_id == Product.id).order_by(Product.price)
    
    elif sort_by == "H-L":
        # order by prod.price desc
        product_query = db.session.query(Product, Cart).outerjoin(Cart, Cart.prod_id == Product.id).order_by(Product.price.desc())


    if not search:
        products = product_query.paginate(
            page=page, per_page=MAX_ITEMS_PER_PAGE)
    else:
        products = product_query.filter(
            Product.title.ilike(f"%{search}%") |
            Product.category.ilike(f"%{search}%")
        ).paginate(page=page, per_page=MAX_ITEMS_PER_PAGE)

    return render_template("products/list-products.html", products=products, categories=get_categories(), search=search, query=query, sort_by=sort_by)


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
    query = []

    if g.user:
        query = db.session.query(Product, Cart).join(
            Cart, Product.id == Cart.prod_id).all()

    category = deslugify(category)
    products = db.session.query(Product, Cart).outerjoin(Cart, Cart.prod_id == Product.id).filter(
        Product.category == category).paginate(page=page, per_page=MAX_ITEMS_PER_PAGE)

    return render_template("products/list-products.html", products=products, category=category, categories=get_categories(), query=query)

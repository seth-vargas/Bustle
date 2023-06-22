from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

bcrypt = Bcrypt()
db = SQLAlchemy()


class Cart(db.Model):
    """ Cart model """

    __tablename__ = "cart"

    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
    prod_id = db.Column(db.Text, db.ForeignKey(
        "products.id", ondelete="CASCADE"), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    def __init__(self, user_id, prod_id):
        self.user_id = user_id
        self.prod_id = prod_id

    @classmethod
    def get_instance(cls, user):
        """ Returns one Cart object in the logged-in users cart """

        return db.session.query(Cart).join(Product, Cart.prod_id == Product.id).filter(Cart.user_id == user.id).one()


favorites_table = db.Table(
    "favorites",
    db.Column("user_id", db.ForeignKey("users.id", ondelete="CASCADE")),
    db.Column("product_id", db.ForeignKey("products.id", ondelete="CASCADE"))
)


class User(db.Model):
    """ User Model """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    num_items_in_cart = db.Column(db.Integer, nullable=False, default=0)
    cart_total_price = db.Column(db.Float, nullable=False, default=0)
    # cart = db.relationship("Product", secondary="cart", lazy="joined")
    cart = db.relationship("Cart", lazy="joined", backref="user")
    favorites = db.relationship(
        "Product", secondary="favorites", lazy="joined")

    @classmethod
    def signup(cls, first_name, last_name, email, password):
        """ Hashes password and adds user to system. """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(first_name=first_name, last_name=last_name,
                    email=email, password=hashed_pwd)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, email, password):
        """
        Searches for a user whose password hash matches this password.
        If it finds such a user, returns that user object. 
        If not found, it returns false.
        """

        user = cls.query.filter_by(email=email).first()

        if user:
            is_authenticated = bcrypt.check_password_hash(
                user.password, password)
            if is_authenticated:
                return user

        return False

    @classmethod
    def change_password(cls, email, password):
        """ Hashes new password and updates user in system """

        user = cls.query.filter_by(email=email).first()
        new_hashed_pwd = bcrypt.generate_password_hash(
            password).decode('UTF-8')
        user.password = new_hashed_pwd

        return user

    def get_full_name(self):
        """ Gets logged-in users first and last name """

        return f"{self.first_name} {self.last_name}"

    def get_num_items_in_cart(self):
        """ Returns an INT value of the number of items the logged-in user has in their cart """

        return db.session.query(func.sum(Cart.quantity)).filter(Cart.user_id == self.id).scalar() or 0

    def get_cart(self):
        """ 
        Returns a LIST of TUPLES, where each tuple contains (<Product>, <Cart>) objects.
        The list is filtered to contain tuples that have a relationship with the logged-in user.
        """

        return db.session.query(Product, Cart).join(Cart, Product.id == Cart.prod_id).filter(Cart.user_id == self.id)

    def get_subtotal(self):
        """ Returns an INT value of the total price of the logged-in users cart """

        return db.session.query(func.sum(Product.price)).join(Cart, Product.id == Cart.prod_id).filter(Cart.user_id == self.id).scalar() or 0


class Product(db.Model):
    """ Product Model """

    __tablename__ = "products"

    id = db.Column(db.Text, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, nullable=False, default=0)
    rate_count = db.Column(db.Integer, nullable=False, default=0)

    def get_product_quantity(self, user):
        """ Returns an INT value representing the quantity of a given item in the users cart """
        
        # product = cls.query.get(self.id)
        quantity =  db.session.query(Cart.quantity).filter(Cart.prod_id == self.id, Cart.user_id == user.id).scalar()

        return quantity

    def slugify(self):
        """ turns sloppy plain text into URL friendly route """

        return self.category.replace(" ", "-")


def get_categories():
    """ returns categories as a list """

    categories = set()

    for prod in Product.query.all():
        categories.add(prod.category)

    return categories


def deslugify(category):
    """ turns URL friendly route into sloppy plain text """

    return category.replace("-", " ")


def connect_db(app):
    """ initializes db in app """

    db.app = app
    db.init_app(app)


# def get_query(sort_by, category=None):
#     base_query = db.session.query(Product, Cart).outerjoin(
#         Cart, Cart.prod_id == Product.id)

#     if category != None:
#         base_query = base_query.filter(Product.category == category)

#     ordered_query = base_query.order_by(Product.id)

#     if sort_by == "A-Z":
#         ordered_query = base_query.order_by(Product.title)

#     elif sort_by == "Z-A":
#         ordered_query = base_query.order_by(Product.title.desc())

#     elif sort_by == "Low-High":
#         ordered_query = base_query.order_by(Product.price)

#     elif sort_by == "High-Low":
#         ordered_query = base_query.order_by(Product.price.desc())

#     return ordered_query

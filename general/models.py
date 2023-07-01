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
    def get_instance(cls, user_id, prod_id):
        """ Returns one Cart object in the logged-in users cart """

        return db.session.query(Cart).filter(Cart.user_id == user_id, Cart.prod_id == prod_id).one()
    

    def get_price(self):
        """ gets price of Cart instance """

        product = Product.query.get(self.prod_id)

        qty = self.quantity

        return product.price * qty


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

        # return db.session.query(func.sum(Product.price)).join(Cart, Product.id == Cart.prod_id).filter(Cart.user_id == self.id).scalar() or 0
        subtotal = 0
        for product, instance in self.get_cart():
            total = product.price * instance.quantity
            subtotal += total

        return subtotal


    def get_line_items(self):
        """ Returns a LIST of DICTS that are present in the users cart """

        line_items = []

        for product, cart_instance in self.get_cart().all():
            line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product.title,
                    'images': [product.image]
                },
                'unit_amount': product.price * 100,
            },
            'quantity': cart_instance.quantity,
        })        
        
        return line_items


    def made_purchase(self):
        """ Upon a successful purchase, reset this users cart and num_items_in_cart """

        for p, instance in self.get_cart().all():
            db.session.delete(instance)

        self.num_items_in_cart = 0

        db.session.add(self)
        db.session.commit()

        return


class Product(db.Model):
    """ Product Model """

    __tablename__ = "products"

    id = db.Column(db.Text, primary_key=True)
    title = db.Column(db.Text, nullable=False, default="Coming soon!")
    image = db.Column(db.Text, nullable=False, default="def-img.url")
    description = db.Column(db.Text, nullable=False, default="No description provided")
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

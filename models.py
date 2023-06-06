from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """ initializes db in app """

    db.app = app
    db.init_app(app)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


cart_association = db.Table(
    "cart",
    db.Column("user_id", db.ForeignKey("users.id")),
    db.Column("product_id", db.ForeignKey("products.id"))
)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


favorites_association = db.Table(
    "favorites",
    db.Column("user_id", db.ForeignKey("users.id")),
    db.Column("product_id", db.ForeignKey("products.id"))
)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class User(db.Model):
    """ User Model """

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    first_name = db.Column(
        db.Text,
        nullable=False
    )

    last_name = db.Column(
        db.Text,
        nullable=False
    )

    email = db.Column(
        db.Text,
        nullable=False, unique=True
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    cart = db.relationship(
        "ProductModel", secondary=cart_association)
    
    favorites = db.relationship(
        "ProductModel", secondary=favorites_association)

    @classmethod
    def signup(cls, first_name, last_name, email, password):
        """ Hashes password and adds user to system. """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_pwd,
        )

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
        new_hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        user.password = new_hashed_pwd
        
        return user

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class ProductModel(db.Model):
    """ Product Model """

    __tablename__ = "products"

    id = db.Column(
        db.Text,
        primary_key=True,
    )
    
    title = db.Column(
        db.Text
    )
    
    image = db.Column(
        db.Text
    )
    
    price = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    category = db.Column(
        db.Text,
        nullable=True
    )

    rating = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    rate_count = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    cart = db.relationship(
        "User", secondary=cart_association, backref="products")
    
    @classmethod
    def get_categories(cls):
        """ returns categories as a list """
        
        categories = set()
        
        for prod in cls.query.all():
            categories.add(prod.category)
            
        return categories
    
    def slugify(self):
        """ turns sloppy plain text into URL friendly route """
        
        return self.category.replace(" ", "-")

def deslugify(category):
    """ turns URL friendly route into sloppy plain text """
    
    return category.replace("-", " ")

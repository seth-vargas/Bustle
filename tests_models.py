import os
from unittest import TestCase
from general.models import db, User, Product, Cart
from sqlalchemy.exc import IntegrityError

import stripe
# from general.secrets import stripe_key
stripe.api_key = os.environ.get("stripe_key")

os.environ['DATABASE_URL'] = "postgresql:///capstone-test"
from app import app  # Must go after database_uri has been set


db.drop_all()
db.create_all()


class CartModelTestCase(TestCase):
    """Tests Cart models."""

    def setUp(self):
        """Create test client, add sample data."""

        db.session.rollback()

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        db.session.add(get_user())
        db.session.add(get_product())

        db.session.commit()

    def test_cart_model(self):
        """Does basic model work?"""

        u = User.query.get(1)
        p = Product.query.get("prod_O1lrR24ZCNswI5")
        c = Cart(user_id=u.id, prod_id=p.id)

        db.session.add(c)
        db.session.commit()

        # User should have 1 item in their cart and there should be 1 item in the Cart table
        self.assertEqual(len(Cart.query.all()), 1)
        self.assertEqual(len(u.get_cart().all()), 1)


class FavoritesModelTestCase(TestCase):
    """ Is the favorites table working as expected? """

    def setUp(self):
        """Create test client, add sample data."""

        db.session.rollback()

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        db.session.add(get_user())
        db.session.add(get_product())

        db.session.commit()

    def test_favorites_model(self):
        """ Tests that favorites model is behaving as expected """

        u = User.query.get(1)
        p = Product.query.get("prod_O1lrR24ZCNswI5")
        u.favorites.append(p)

        db.session.commit()

        # check if the length of user.favorites is == 1
        self.assertEqual(len(u.favorites), 1)

    def test_favorites_model_delete(self):
        """ Tests that deleting a model is behaving as expected """

        u = User.query.get(1)
        p = Product.query.get("prod_O1lrR24ZCNswI5")
        u.favorites.append(p)
        u.favorites.remove(p)

        self.assertEqual(len(u.favorites), 0)


class ProductModelTestCase(TestCase):
    """ Tests that model for products is working as expected """

    def setUp(self):
        """Create test client, add sample data."""

        db.session.rollback()

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        db.session.add(get_product())
        db.session.add(get_user())

        db.session.commit()

    def test_get_prod(self):
        """ Does querying work as expected? """

        p = Product.query.get("prod_O1lrR24ZCNswI5")

        self.assertEqual(p.id, "prod_O1lrR24ZCNswI5")
        self.assertEqual(p.price, 13)

    def test_get_product_quantity(self):
        """ should return None since scalars do that in sqlalchemy """

        p = Product.query.get("prod_O1lrR24ZCNswI5")
        u = User.query.get(1)

        qty = p.get_product_quantity(u)

        self.assertEqual(qty, None)

    def test_slugify(self):
        """ slugify should modify the text to be url friendly """

        p = Product.query.get("prod_O1lrR24ZCNswI5")
        category = p.category
        slugified = p.slugify()

        self.assertNotEqual(category, slugified)
        self.assertEqual(slugified, "women's-clothing")


class UserModelTestCase(TestCase):
    """ Does the user model behave as expected? """

    def setUp(self):
        """Create test client, add sample data."""

        db.session.rollback()

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        db.session.add(get_user())
        db.session.add(get_product())

        db.session.commit()

    def test_user_model(self):
        """ When creating a user, does it work as expected? """

        u1 = User(
            first_name="TEST",
            last_name="USER",
            email="TESTUSER1@gmail.com",
            password="SECRET"
        )

        u2 = User(
            first_name="TEST",
            last_name="USER",
            email="TESTUSER2@gmail.com",
            password="SECRET"
        )

        u3 = User(
            first_name="TEST",
            last_name="USER",
            email="TESTUSER3@gmail.com",
            password="SECRET"
        )

        fail_user = User(
            first_name="TEST",
            last_name="USER",
            email="TESTUSER@gmail.com",
            password="SECRET"
        )

        db.session.add_all([u1, u2, u3, fail_user])

        try:
            db.session.commit()

        except Exception as e:
            self.assertEqual(e, IntegrityError)

    def test_get_fullname(self):
        """ does get_full_name work as expected? """

        u = User.query.get(1)

        name = u.get_full_name()

        self.assertEqual(name, "TESTUSER 1")

    def test_authenticate(self):
        """ does authenticate method work as expected? """

        u = User.query.get(1)

        correct = u.authenticate("TEST1@gmail.com", "SECRET_PASSWORD")
        incorrect = u.authenticate("Wrong email", "Wrong password")

        self.assertFalse(incorrect)
        self.assertEqual(correct, u)

    def test_get_num_items_in_cart(self):
        """ does get_num_items_in_cart return an int that we expect? """

        u = User.query.get(1)

        is_zero = u.get_num_items_in_cart()

        for i in range(1, 100):
            p = Product(id=f"prod_{i}")

            db.session.add(p)
            db.session.commit()

        for prod in Product.query.all():
            db.session.add(Cart(user_id=u.id, prod_id=prod.id))
            db.session.commit()

        is_large = u.get_num_items_in_cart()

        self.assertEqual(is_zero, 0)
        self.assertEqual(is_large, 100)

    def test_get_cart(self):
        """ does the get_cart method return a valid tuple """

        u = User.query.get(1)
        p = Product.query.get("prod_O1lrR24ZCNswI5")

        no_items_in_cart = u.get_cart().all()

        c = Cart(u.id, p.id)

        db.session.add(c)
        db.session.commit()

        cart_item = u.get_cart().all()

        self.assertEqual(no_items_in_cart, [])
        self.assertEqual(cart_item, [(p, Cart.query.all()[0])])

    def test_get_line_items(self):
        """ should return a list of line items """

        u = User.query.get(1)

        line_items = u.get_line_items()

        self.assertEqual(len(line_items), 0)


# Helper funcs
def get_product():

    prod = stripe.Product.retrieve("prod_O1lrR24ZCNswI5")
    unit_amount = stripe.Price.retrieve(prod.default_price).unit_amount
    prod.update({"unit_amount": unit_amount})

    return Product(
        id=str(prod.id),
        title=str(prod.name),
        image=str(prod.images[0]),
        description=str(prod.description),
        price=prod.unit_amount / 100,
        category=str(prod.metadata.category),
        rating=float(prod.metadata.rating),
        rate_count=int(prod.metadata.rate_count)
    )


def get_user():
    return User.signup("TESTUSER", "1", "TEST1@gmail.com", "SECRET_PASSWORD")

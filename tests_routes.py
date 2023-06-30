from app import app, CURR_USER_KEY
import os
from unittest import TestCase
from general.models import db, User, Product
from app import app

os.environ["DATABASE_URL"] = "postgresql:///capstone-test"


app.config["WTF_CSRF_ENABLED"] = False

db.drop_all()
db.create_all()


class ProductRoutesTestCase(TestCase):
    """ Tests that product views behave as expected """

    # TODO test_show_all_products
    # TODO test_show_product
    # TODO test_show_products_by_category


class UserRoutesTestCase(TestCase):
    """ Tests that logged in user views behave correctly """

    def setUp(self):
        """ Create test client """

        db.session.rollback()

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(
            first_name="TEST",
            last_name="USER",
            email="TESTUSER1@gmail.com",
            password="PASSWORD")

        db.session.commit()

    def test_show_account(self):
        """ Logged in user views account """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/my-account")
            text = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="text-center">My Account</h1>', text)

    def test_edit_account(self):
        """ GET to /my-account/edit """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/my-account/edit")
            text = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h1>Update your account</h1>', text)

    def test_user_change_password(self):
        """ Test that GET for /my-account/change-password is functioning as expected """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/my-account/change-password")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h1>Change your password</h1>",
                          resp.get_data(as_text=True))

    def test_show_cart(self):
        """ Does GET request to /cart work as expected? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get("/cart")

        self.assertEqual(resp.status_code, 200)
        self.assertIn("You have nothing in your cart!",
                      resp.get_data(as_text=True))

    def test_show_favorites(self):
        """ Does getting the favorites work as expected? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get("/favorites")

        self.assertEqual(resp.status_code, 200)
        self.assertIn("You have nothing in your favorites.",
                      resp.get_data(as_text=True))

    def test_show_success_page(self):
        """ Does user get returned to success page? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get("/success")

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            "<h1>Thanks for your order!</h1>" in resp.get_data(as_text=True))

    def test_logged_out_users_views(self):
        """ Tests that users who are not logged in are not able to see these routes """

        blocked_routes = [
            "/my-account",
            "/my-account/edit",
            "/my-account/change-password",
            "/cart",
            "/favorites",
            "success"
        ]

        with self.client as c:
            for route in blocked_routes:

                resp = c.get(route)

                self.assertNotEqual(resp.status_code, 200)
                self.assertIn("/login", resp.location)

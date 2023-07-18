from app import db
from general.models import User, Product, Cart
import requests
import stripe
# from general.secrets import stripe_key
import os
stripe.api_key = os.environ.get("stripe_key")


def setup_db():
    db.drop_all()
    db.create_all()


def fetch_products():
    """ gets products from stripe api and stores on local db """

    products = stripe.Product.list(limit=20)

    for prod in products.data:
        unit_amount = stripe.Price.retrieve(prod.default_price).unit_amount
        prod.update({"unit_amount": unit_amount})

        db.session.add(Product(
            id=str(prod.id),
            title=str(prod.name),
            image=str(prod.images[0]),
            description=str(prod.description),
            price=prod.unit_amount / 100,
            category=str(prod.metadata.category),
            rating=float(prod.metadata.rating),
            rate_count=int(prod.metadata.rate_count)
        ))
        db.session.commit()


def post_new_products():
    """ Creates new products in stripes api """
    request = requests.get("https://fakestoreapi.com/products")

    for product in request.json():
        prod = stripe.Product.create(
            name=product["title"],
            description=product["description"],
            images=[product["image"]],
            metadata={
                "rating": product["rating"]["rate"],
                "rate_count": product["rating"]["count"],
                "category": product["category"]
            }
        )

        price = stripe.Price.create(
            product=f"{prod.id}",
            currency="usd",
            unit_amount=int(float(product["price"])*100)
        )

        stripe.Product.modify(
            prod.id,
            default_price=price.id
        )


def create_users():
    user1 = User.signup("seth", "vargas", "sv@gmail.com", "Password")
    user2 = User.signup("kaitlyn", "vargas", "kv@gmail.com", "Password")

    db.session.add_all([user1, user2])
    db.session.commit()


def create_carts():
    products = Product.query.all()
    user = User.query.get(1)
    db.session.add(Cart(user_id=user.id, prod_id=products[0].id))
    db.session.add(Cart(user_id=user.id, prod_id=products[1].id))
    db.session.commit()


if __name__ == "__main__":
    try:            
        print("Setting up db...")
        setup_db()
        print("getting products...")
        fetch_products()
        print("creating users...")
        create_users()
        print("creating carts...")
        create_carts()
        print("Done!!")

    except Exception as e:
        print(e)
from app import db
from models import User, ProductModel, cart_association, favorites_association
import requests
import stripe
from secrets import stripe_key
stripe.api_key = stripe_key


db.drop_all()
db.create_all()

# Code to insert tables here
request = requests.get("https://fakestoreapi.com/products")
products = []
    
for product in request.json():
    prod = stripe.Product.create(
        name=product["title"],
        description=product["description"],
        images=[product["image"]],
    )
    
    price = stripe.Price.create(
        product=f"{prod.id}",
        currency="usd",
        unit_amount=int(float(product["price"])*100)
    )
    
    prod.default_price = ( stripe.Price.retrieve(price.id).unit_amount ) / 100
    
    # products.append(ProductModel(
    #     id=prod.id,
    #     price=prod.default_price,
    #     category=product["category"],
    #     rating=product["rating"]["rate"],
    #     rate_count=product["rating"]["count"]
    # ))
    
    
user = User.signup("seth", "vargas", "sv@gmail.com", "Password")

db.session.add_all(products)
db.session.add(user)
db.session.commit()

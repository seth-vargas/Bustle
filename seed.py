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
    
for product in request.json():
    prod = stripe.Product.create(
        name=product["title"],
        description=product["description"],
        images=[product["image"]],
        metadata={
            "rating": product["rating"]["rate"],
            "rate_count": product["rating"]["count"]
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
    
    
user = User.signup("seth", "vargas", "sv@gmail.com", "Password")

db.session.add(user)
db.session.commit()

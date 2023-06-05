from app import db
from models import User, Product, cart_association, favorites_association
import requests


db.drop_all()
db.create_all()

# Code to insert tables here
request = requests.get("https://fakestoreapi.com/products")
products = []

for r in request.json():
    products.append(Product(
        title=r["title"],
        price=r["price"],
        description=r["description"],
        category=r["category"],
        image=r["image"],
        rating=r["rating"]["rate"],
        rate_count=r["rating"]["count"]
    ))
    
user = User.signup("seth", "vargas", "sv@gmail.com", "Password")

db.session.add_all(products)
db.session.add(user)
db.session.commit()

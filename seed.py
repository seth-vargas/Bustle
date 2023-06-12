from app import db
from models import User, Product, cart_association, favorites_association
import requests
import stripe
from secrets import stripe_key
stripe.api_key = stripe_key


db.drop_all()
# breakpoint()
print("Dropped tables")

db.create_all()

# Code to insert tables here:
# request = requests.get("https://fakestoreapi.com/products")
    
# for product in request.json():
#     prod = stripe.Product.create(
#         name=product["title"],
#         description=product["description"],
#         images=[product["image"]],
#         metadata={
#             "rating": product["rating"]["rate"],
#             "rate_count": product["rating"]["count"],
#             "category": product["category"]
#         }
#     )
    
#     price = stripe.Price.create(
#         product=f"{prod.id}",
#         currency="usd",
#         unit_amount=int(float(product["price"])*100)
#     )
    
#     stripe.Product.modify(
#         prod.id,
#         default_price=price.id
#     )
    
# Loop over prods.data and store in db on server side
products = stripe.Product.list(limit=20)

for prod in products.data:
    unit_amount = stripe.Price.retrieve(prod.default_price).unit_amount
    prod.update({"unit_amount": unit_amount})
    
    db.session.add(Product(
        id=str(prod.id),
        title=str(prod.name),
        image=str(prod.images[0]),
        price=int(prod.unit_amount / 100),
        category=str(prod.metadata.category),
        rating=float(prod.metadata.rating),
        rate_count=int(prod.metadata.rate_count)
    ))
    

    
user = User.signup("seth", "vargas", "sv@gmail.com", "Password")

db.session.add(user)
db.session.commit()

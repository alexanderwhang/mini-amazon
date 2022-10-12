from app.models.order import Order
from app.models.product import Product
from app.models.purchase import Purchase
from app import create_app

if __name__ == "__main__":
    app = create_app()
    a = Purchase.get_all_purchases_by_user(0)
    print(a)
from flask import render_template
from flask_login import current_user
import datetime

from .models.product import Product
from .models.order import Order
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    # Get purchases by product id
    purchases0 = Purchase.get_all_purchases_by_order(0)
    # Get purchases by user id
    all_user_purchase = Purchase.get_all_purchases_by_user(0)
    # get all available products for sale:
    products = Product.get_all(True)
    # find the products current user has bought:
    if current_user.is_authenticated:
        orders = Order.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        orders = None
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,
                           purchase_history=orders,
                           all_purchases = purchases0,
                           all_user_purchase = all_user_purchase)
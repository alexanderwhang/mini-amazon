from flask import render_template
from flask_login import current_user
import datetime

from .models.product import Product
from .models.order import Order
from .models.purchase import Purchase
from .models.user import User
from .models.review import Review

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    # get all available products for sale:
    products = Product.get_all()
    # find the products current user has bought:
    if current_user.is_authenticated:
        orders = Purchase.get_all_purchases_by_user(Purchase.user_email_to_id(current_user.email))
        reviews = Review.get_all_by_uid(Review.user_email_to_id(current_user.email))
        # print(current_user.email)
    else:
        orders = None
        reviews = None
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,
                           purchase_history=orders,
                           all_products = products,
                           all_user_reviews = reviews)
from flask import render_template
from flask_login import current_user
import datetime

from .models.product import Product
from .models.order import Order
from .models.purchase import Purchase
from .models.user import User

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/seller')
def seller():
    # get all available products for sale:
    inventory = Inventory.get_all_inventories_by_user(current_user.id)
    fulfillment = Fulfillment.get_all_fulfillment_by_user(current_user.id)
    # find the products current user has bought:
    #if current_user.is_authenticated:
    #    orders = Purchase.get_all_purchases_by_user(Purchase.user_email_to_id(current_user.email))
        # print(current_user.email)

    # render the page by adding information to the index.html file
    return render_template('inventoryFulfillment.html',
                           purchase_history=orders,
                           all_products = inventory)
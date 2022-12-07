
from flask import current_app as app
from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request
bp = Blueprint('purchase', __name__)
from .models.order import Orders
from .models.purchase import Purchase, OrderPrice

@bp.route('/purchase/<oid>', methods=['GET', 'POST'])
def purchase(oid=None):
    status = 'Fulfilled'
    purchases = Purchase.get_all_purchases_by_order(oid)
    totalPrice = float(OrderPrice.getPrice(oid))
    discountedTotalPrice = float(Orders.getOrderPrice(oid))
    discountFactor = discountedTotalPrice/totalPrice
    for purch in purchases:
        
        purch.product_price = "{:0.2f}".format(float(purch.product_price) * discountFactor)
        purch.total_price = "{:0.2f}".format(float(purch.total_price) * discountFactor)
        if purch.fulfillment_status == 'shipped' or purch.fulfillment_status == 'ordered':
            status = 'Pending'
            break

    return render_template('purchase.html', title='Purchase', purchases=purchases, totalPrice=discountedTotalPrice, status=status)
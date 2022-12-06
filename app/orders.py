from flask import current_app as app
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from flask_login import current_user
from .models.user import User, BadUpdateException
from .models.purchase import Purchase
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
bp = Blueprint('orders', __name__)

# ORDERS PAGE:

# the Orders class has all the componenets to load the orders for a user on our ecommerce site
class Orders:
    def __init__(self, oid, uid, tot_price, tot_items, time):
        self.oid = oid
        self.uid = uid
        self.tot_price = tot_price
        self.tot_items = tot_items
        self.time = time

    # this method gets all of the orders from a specific user
    @staticmethod
    def get_all_orders_by_user(user_id):
        rows = app.db.execute('''
SELECT id, user_id, total_price, total_items, time_stamp
FROM Orders
WHERE user_id = :user_id
''',
                              user_id=user_id)
        return [Orders(*row) for row in rows]

# orders loads all the relevant information from the database
@bp.route('/orders', methods=['GET', 'POST'])
def orders():
    fulfillmentDict = {} # dictionary to keep track of fulfillment
    user = User.get(current_user.id) # gets the user information
    orders = Orders.get_all_orders_by_user(current_user.id) # gets order information by user

    # iterates through each order
    for o in orders:
        purchases = Purchase.get_all_purchases_by_order(o.oid) # gets the purchases of each order
        
        # iterates through each purchase
        for purch in purchases:
            # if the fulfillment status of a purchase is shipped or
            # ordered, set the fulfillment status of that order to pending
            if purch.fulfillment_status == 'shipped' or purch.fulfillment_status == 'ordered':
                fulfillmentDict[o.oid] = 'Pending'
                break

            # otherwise, set the status to fulfilled (meaning all purchases are delivered)
            fulfillmentDict[o.oid] = 'Fulfilled'

    # load orders html template
    return render_template('orders.html', title='Orders', user=user, orders=orders, fulfillmentDict=fulfillmentDict)
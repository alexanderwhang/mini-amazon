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

class Orders:
    def __init__(self, oid, uid, tot_price, tot_items, time):
        self.oid = oid
        self.uid = uid
        self.tot_price = tot_price
        self.tot_items = tot_items
        self.time = time

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, user_id, total_price, total_items, time_stamp
FROM Orders
WHERE id = :id
''',
                              id=id)
        return Orders(*(rows[0])) if rows else None

    @staticmethod
    def get_all_orders_by_user(user_id):
        rows = app.db.execute('''
SELECT id, user_id, total_price, total_items, time_stamp
FROM Orders
WHERE user_id = :user_id
''',
                              user_id=user_id)
        return [Orders(*row) for row in rows]

@bp.route('/orders', methods=['GET', 'POST'])
def orders():
    fulfillmentDict = {}
    user = User.get(current_user.id)
    orders = Orders.get_all_orders_by_user(current_user.id)

    for o in orders:
        purchases = Purchase.get_all_purchases_by_order(o.oid)
        for purch in purchases:
            if purch.fulfillment_status == 'shipped' or purch.fulfillment_status == 'ordered':
                fulfillmentDict[o.oid] = 'Pending'
                break
            fulfillmentDict[o.oid] = 'Fulfilled'

    return render_template('orders.html', title='Orders', user=user, orders=orders, fulfillmentDict=fulfillmentDict)
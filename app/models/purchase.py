from flask import current_app as app
from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request
bp = Blueprint('purchase', __name__)


class Purchase:
    def __init__(self, order_id, product_name, product_price, quantity, total_price, fulfillment_status):
        self.order_id = order_id
        self.product_name = product_name #from product
        self.product_price= product_price #from product
        self.quantity = quantity
        self.total_price = total_price #calc'd from product
        self.fulfillment_status = fulfillment_status

    @staticmethod
    def get_all_purchases_by_user(user_id):
        rows = app.db.execute('''
with userOrders as (
    SELECT order_id
    from Orders
    WHERE user_id = :user_id
)
select 
    userOrders.order_id as order_id, 
    Products.name as product_name, 
    Products.price as product_price, 
    Purchases.quantity as quantity, 
    Purchases.quantity*Products.price as total_price,
    Purchases.fulfillment_status as fulfillment_status
from 
    userOrders, 
    Products, 
    Purchases
where 
    Purchases.order_id = userOrders.order_id
    and Purchases.pid = Products.product_id
''',
                              user_id=user_id)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def user_email_to_id(user_email):
        rows = app.db.execute(
            """
            SELECT user_id
            FROM Users
            WHERE email = :user_email
            """,
            user_email=user_email
        )
        return rows[0][0]

    @staticmethod
    def get_all_purchases_by_order(order_id):
        rows = app.db.execute('''
select 
    order_id as order_id, 
    Products.name as product_name, 
    Products.price as product_price, 
    Purchases.quantity as quantity, 
    Purchases.quantity*Products.price as total_price,
    Purchases.fulfillment_status as fulfillment_status
from 
    Products, 
    Purchases
where 
    Purchases.order_id = :order_id
    and Purchases.pid = Products.product_id
''',
                              order_id=order_id)
        return [Purchase(*row) for row in rows]

class OrderPrice:
    def __init__(self, price):
        self.price = price

    @staticmethod
    def getPrice(oid):
        price = app.db.execute('''
SELECT SUM(Products.price * Purchases.quantity)
FROM Products, Purchases
WHERE Purchases.order_id = :oid
AND Purchases.pid = Products.product_id
''',
                              oid=oid)
        if str(*price[0]) == 'None':
            return "This order contains no items!"
        return "Total price: $"+str(*price[0])

@bp.route('/purchase/<oid>', methods=['GET', 'POST'])
def purchase(oid=None):
    purchases = Purchase.get_all_purchases_by_order(oid)
    totalPrice = OrderPrice.getPrice(oid)
    return render_template('purchase.html', title='Purchase', purchases=purchases, totalPrice=totalPrice)
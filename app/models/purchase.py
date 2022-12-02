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
    def get_all_purchases_by_user(user_id, datefilter=None,keyword=None):
        interval = "" #finds all historic purchases
        keywordSearch = "" #finds all purchases
        if datefilter is not None:
            if datefilter=='month':
                interval = "and time_stamp >= current_date - interval '1 months'"
            elif datefilter=='3month':
                interval = "and time_stamp >= current_date - interval '3 months'"
            elif datefilter=='year':
                interval = "and time_stamp >= current_date - interval '1 years'"
        
            

        if keyword is not None:
            keywordSearch = f"and Products.name like '%{keyword}%'"

        rows = app.db.execute(f'''
        with userOrders as (
            SELECT id as order_id
            from Orders
            WHERE user_id = :user_id
            {interval}
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
            and Purchases.pid = Products.id
            {keywordSearch}
        ''',
                              user_id=user_id)
        return [Purchase(*row) for row in rows]


    @staticmethod
    def user_email_to_id(user_email):
        rows = app.db.execute(
            """
            SELECT id
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
    and Purchases.pid = Products.id
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
AND Purchases.pid = Products.id
''',
                              oid=oid)
        if str(*price[0]) == 'None':
            return "This order contains no items!"
        return "Total price: $"+str(*price[0])

@bp.route('/purchase/<oid>', methods=['GET', 'POST'])
def purchase(oid=None):
    status = 'Fulfilled'
    purchases = Purchase.get_all_purchases_by_order(oid)
    for purch in purchases:
        if purch.fulfillment_status == 'shipped' or purch.fulfillment_status == 'ordered':
            status = 'Pending'
            break

    totalPrice = OrderPrice.getPrice(oid)
    return render_template('purchase.html', title='Purchase', purchases=purchases, totalPrice=totalPrice, status=status)
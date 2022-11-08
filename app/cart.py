from flask import current_app as app
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from flask_login import current_user
from .models.user import User, BadUpdateException
from flask import Blueprint
bp = Blueprint('cart', __name__)

class Cart:
    """
    This is just a TEMPLATE for Cart, you should change this by adding or 
        replacing new columns, etc. for your design.
    """
    def __init__(self, id, uid, pid, name, price, quantity, time_added_to_cart):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.name = name
        self.price = price
        self.quantity = quantity
        self.time_added_to_cart = time_added_to_cart

# get and get_all_by_uid_since queries outdated

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, quantity, time_added_to_cart
FROM Cart
WHERE id = :id
''',
                              id=id)
        return Cart(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, uid, pid, quantity, time_added_to_cart
FROM Cart
WHERE uid = :uid
AND time_added_to_cart >= :since
ORDER BY time_added_to_cart DESC
''',
                              uid=uid,
                              since=since)
        return [Cart(*row) for row in rows]

    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT Cart.user_id, Cart.product_id, Products.name, Products.price, quantity, time_added_to_cart
FROM Cart, Products
WHERE uid = :uid
AND Cart.pid = Products.id
ORDER BY time_added_to_cart DESC
''',
                              uid=uid)
        return [Cart(*row) for row in rows]

class CartPrice:
    def __init__(self, price):
        self.price = price

    @staticmethod
    def getPrice(uid):
        price = app.db.execute('''
SELECT SUM(price * quantity)
FROM Cart, Products
WHERE uid = :uid
AND Carts.pid = Products.id
''',
                              uid=uid)
        return "$"+str(*price[0])

@bp.route('/cart')
def cart():
    user = User.get(current_user.id)
    cart = Cart.get_all_by_uid(current_user.id)
    return render_template('cart.html', title='Cart', user=user)
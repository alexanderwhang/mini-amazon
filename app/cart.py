from flask import current_app as app
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from flask_login import current_user
from .models.user import User, BadUpdateException
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
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
SELECT Carts.id, uid, pid, name, price, Carts.quantity, time_added_to_cart
FROM Carts, Products
WHERE uid = :uid
AND Carts.pid = Products.product_id
ORDER BY time_added_to_cart DESC
''',
                              uid=uid)
        return [Cart(*row) for row in rows]
    
    @staticmethod
    def get_pid_from_uid_cart(uid, pid):
        rows = app.db.execute('''
SELECT id, uid, pid, quantity, time_added_to_cart
FROM Carts
WHERE uid = :uid
AND pid = :pid
''',
                              uid=uid,
                              pid=pid)
        return [Cart(*row) for row in rows]

class CartPrice:
    def __init__(self, price):
        self.price = price

    @staticmethod
    def getPrice(uid):
        price = app.db.execute('''
SELECT SUM(price * Carts.quantity)
FROM Carts, Products
WHERE uid = :uid
AND Carts.pid = Products.product_id
''',
                              uid=uid)
        if str(*price[0]) == 'None':
            return "Your cart is empty!"
        return "Total cart price: $"+str(*price[0])

@bp.route('/cart', methods=['GET', 'POST'])
@bp.route('/cart/<action>/<uid>/<pid>', methods=['GET', 'POST'])
def cart(action=None, uid=None, pid=None, quantity=1):
    user = User.get(current_user.id)
    cart = Cart.get_all_by_uid(current_user.id)
    totalPrice = CartPrice.getPrice(current_user.id)
    quantities = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    
    if request.method == "POST":
        if action == 'delete':
            app.db.execute('''DELETE FROM Carts
            WHERE uid = :uid AND pid = :pid''', uid=uid, pid=pid)
            return redirect(url_for('cart.cart'))
        
        if action == 'update':
            app.db.execute('''UPDATE Carts
            SET quantity = :quantity
            WHERE uid = :uid AND pid = :pid''', uid=uid, pid=pid, quantity=request.form['quant'])
            return redirect(url_for('cart.cart'))
        
    elif request.method == "GET":
        return render_template('cart.html', title='Cart', user=user, cart=cart, totalPrice=totalPrice, quantities=quantities)
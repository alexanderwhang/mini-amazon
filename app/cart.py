from flask import current_app as app
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_login import current_user
from .models.user import User, BadUpdateException
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
bp = Blueprint('cart', __name__)

# CARTS PAGE:

# the Cart class has all the components to load the cart for a user on our ecommerce site
class Cart:
    def __init__(self, id, uid, pid, name, price, quantity, time_added_to_cart):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.name = name
        self.price = price
        self.quantity = quantity
        self.time_added_to_cart = time_added_to_cart

    # this method gets all of the items in a specific user's cart
    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT Carts.id, uid, pid, name, price, Carts.quantity, time_added_to_cart
FROM Carts, Products
WHERE uid = :uid
AND Carts.pid = Products.id
ORDER BY time_added_to_cart DESC
''', uid=uid)
        return [Cart(*row) for row in rows]

    # this method gets a specific item in a specific user's cart
    @staticmethod
    def get_pid_from_uid_cart(uid, pid):
        rows = app.db.execute('''
SELECT id, uid, pid, quantity, time_added_to_cart
FROM Carts
WHERE uid = :uid
AND pid = :pid
''', uid=uid, pid=pid)
        return [Cart(*row) for row in rows]

# the CartPrice class initializes the total price of a user's cart
class CartPrice:
    def __init__(self, price):
        self.price = price

    # this method calculates the total price of a user's cart by multiplying
    # the price and quantity of each item in the cart and summing the result
    @staticmethod
    def getPrice(uid):
        price = app.db.execute('''
SELECT SUM(price * Carts.quantity)
FROM Carts, Products
WHERE uid = :uid
AND Carts.pid = Products.id
''', uid=uid)

        # if the cart is empty (nothing is returned), return $0
        if str(*price[0]) == 'None':
            return "0.00"
        return str(*price[0])
    
    @staticmethod
    def getDiscountedPrice(price):
        return str(price)

class Coupon(FlaskForm):
    coupon = StringField('Promotional Coupon Code:', validators=[])

# cart loads all the relevant information from the database
@bp.route('/cart', methods=['GET', 'POST'])
@bp.route('/cart/<action>/<uid>/<pid>', methods=['GET', 'POST'])
@bp.route('/cart/<action>/<uid>', methods=['GET', 'POST'])
def cart(action=None, uid=None, pid=None, quantity=1):
    user = User.get(current_user.id) # gets the user information
    cart = Cart.get_all_by_uid(current_user.id) # loads the user's cart

    totalPrice = CartPrice.getPrice(current_user.id) # loads the total price of the user's cart

    quantities = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'] # allows a user to buy up to 10 of an item if needed

    # the posting methods allow for customizability of user's cart including deleting items, updating quantities,
    # saving items for later, and ordering the contents of their cart
    if request.method == "POST":

        # allows users to delete items from their cart
        if action == 'delete':
            app.db.execute('''DELETE FROM Carts
            WHERE uid = :uid AND pid = :pid
            ''', uid=uid, pid=pid)
            return redirect(url_for('cart.cart'))
        
        # allows users to update the quantity of an item
        if action == 'update':
            app.db.execute('''UPDATE Carts
            SET quantity = :quantity
            WHERE uid = :uid AND pid = :pid
            ''', uid=uid, pid=pid, quantity=request.form['quant'])
            return redirect(url_for('cart.cart'))
        
        # allows users to save items for later in a separate 'Saved For Later' page
        if action == 'save':
            # delete item from the cart
            app.db.execute('''DELETE FROM Carts
            WHERE uid = :uid AND pid = :pid
            ''', uid=uid, pid=pid)

            # add item to saved for later
            app.db.execute('''INSERT INTO Saved (uid, pid, time)
            VALUES (:uid, :pid, current_timestamp(0))
            ''', uid=uid, pid=pid)
            return redirect(url_for('cart.cart'))

    # load cart html template
    elif request.method == "GET":
        return render_template('cart.html', title='Cart', user=user, cart=cart, totalPrice=totalPrice, quantities=quantities)
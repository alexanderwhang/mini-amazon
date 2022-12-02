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
AND Carts.pid = Products.id
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
AND Carts.pid = Products.id
''',
                              uid=uid)
        if str(*price[0]) == 'None':
            return "Your cart is empty!"
        return str(*price[0])

@bp.route('/cart', methods=['GET', 'POST'])
@bp.route('/cart/<action>/<uid>/<pid>', methods=['GET', 'POST'])
@bp.route('/cart/<action>/<uid>', methods=['GET', 'POST'])
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
        
        if action == 'confirm':
            unavailable = []
            rows = app.db.execute('''
            SELECT
                U.balance as bal,
                C.quantity as needed,
                P.quantity as have,
                P.available as avail,
                C.pid as pid,
                P.price as price
            FROM Products P, Carts C, Users U
            WHERE C.pid = P.id
            AND C.uid = :uid
            AND U.id = :uid
            AND U.balance >= :totalPrice
            ''', uid=uid, totalPrice=totalPrice)
            
            if len(rows) == 0:
                return "You do not have enough money"
            else:
                for row in rows:
                    if row.needed > row.have:
                        unavailable.append(row.pid)
                if len(unavailable) != 0:
                    return "One or more items in your cart have limited stock!"
                else:
                    totalItems = len(rows)
                    #push cart to orders table
                    seq = app.db.execute('''SELECT MAX(id)+1 FROM Orders''')
                    oid = int(*seq[0])
                    app.db.execute('''INSERT INTO Orders (id, user_id, total_price, total_items, time_stamp)
                    VALUES (:oid, :uid, :totalPrice, :totalItems, current_timestamp)''', 
                    oid=oid, uid=uid, totalPrice=totalPrice, totalItems=totalItems)

                    
                    for row in rows:
                        #push each cart item to purchases table
                        app.db.execute('''INSERT INTO Purchases (order_id, pid, quantity, fulfillment_status)
                        VALUES (:oid, :pid, :quantity, 'ordered')''',
                        oid=oid, pid=row.pid, quantity=row.needed)

                        #update stock available
                        app.db.execute('''UPDATE Products SET quantity = :quantity
                        WHERE id = :pid''', pid=row.pid, quantity=row.have-row.needed)

                        #update seller balance
                        getSeller = app.db.execute('''SELECT user_id
                        FROM Products
                        WHERE id = :pid''',
                        pid=row.pid)
                        seller_uid = int(*getSeller[0])
                        seller = User.get(seller_uid)
                        balance = float(seller.balance) + float(row.needed*row.price)
                        app.db.execute('''UPDATE Users SET balance = :balance
                        WHERE id = :uid''', uid=seller_uid, balance=balance)
                    
                    #update buyer and seller balances
                    buyerBalance = float(user.balance) - float(totalPrice)
                    app.db.execute('''UPDATE Users SET balance = :balance
                    WHERE id = :uid''', uid=uid, balance=buyerBalance)
                    
                    #delete everything in cart
                    app.db.execute('''DELETE FROM Carts
                    WHERE uid = :uid''', uid=uid)
                    return redirect(url_for('cart.cart'))

    elif request.method == "GET":
        return render_template('cart.html', title='Cart', user=user, cart=cart, totalPrice=totalPrice, quantities=quantities)

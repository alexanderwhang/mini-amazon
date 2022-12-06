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
    couponDict = {'a': 0.1, 'HOLIDAYS': 0.8, 'WINTER22': 0.78, '20OFF': 0.8, 'HALFOFF': 0.5}

    form = Coupon()
    
    # the posting methods allow for customizability of user's cart including deleting items, updating quantities,
    # saving items for later, and ordering the contents of their cart
    if request.method == "POST":

        if action == 'coupon':
            if form.validate_on_submit:
                code = form.coupon.data.strip()
                if code in couponDict:
                    multiplier = couponDict[code]
                    discountedPrice = '%.2f' % (multiplier * float(totalPrice))
                else:
                    flash('Invalid coupon code!')
                    return redirect(url_for('cart.cart'))

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
            WHERE uid = :uid AND pid = :pid''', uid=uid, pid=pid)

            # add item to saved for later
            app.db.execute('''INSERT INTO Saved (uid, pid, time)
            VALUES (:uid, :pid, current_timestamp(0))
            ''', uid=uid, pid=pid)
            return redirect(url_for('cart.cart'))
        
        # allows users to order what is in their cart
        if action == 'confirm':
            # if nothing is in the cart, nothing happens
            if len(cart) == 0:
                flash('Add items to your cart before ordering!')
                return redirect(url_for('cart.cart'))
            
            unavailable = []

            # this query checks to see if a user has enough to pay for the order
            # as well as shows the quantities wanted and available for each item
            rows = app.db.execute('''
            SELECT
                U.balance as bal,
                C.quantity as needed,
                P.quantity as have,
                P.available as avail,
                C.pid as pid,
                P.name as name,
                P.price as price
            FROM Products P, Carts C, Users U
            WHERE C.pid = P.id
            AND C.uid = :uid
            AND U.id = :uid
            AND U.balance >= :totalPrice
            ''', uid=uid, totalPrice=totalPrice)
            
            # if the query is empty, this means that the user cannot pay for the entire order
            # the user is redirected to a page where they can see their balance and the cart price
            if len(rows) == 0:
                return render_template('balanceerror.html', totalPrice=totalPrice, user=user)
            else:
                # iterates through each item
                for row in rows:
                    # if the quantity of an item exceeds the available quantity, add the pid
                    # to a dictionary
                    if row.needed > row.have:
                        unavailable.append(row)
                
                # if the dictionary is not empty, this means that one item has less stock than
                # the quantity that is trying to be bought
                if len(unavailable) != 0:
                    return render_template('stockerror.html', user=user, unavailable=unavailable)
                else: # the dictionary is empty and every item is available at the quantity the user has ordered
                    totalItems = len(rows)
                    
                    # add the details of the order to the Orders table
                    oid = app.db.execute('''INSERT INTO Orders (user_id, total_price, total_items, time_stamp)
                    VALUES (:uid, :totalPrice, :totalItems, current_timestamp(0))
                    RETURNING id
                    ''', uid=uid, totalPrice=totalPrice, totalItems=totalItems)[0][0]

                    # iterating through each item in the order
                    for row in rows:
                        # add each item to the Purchases table
                        app.db.execute('''INSERT INTO Purchases (order_id, pid, quantity, fulfillment_status)
                        VALUES (:oid, :pid, :quantity, 'ordered')
                        ''', oid=oid, pid=row.pid, quantity=row.needed)

                        # decrement stock available
                        app.db.execute('''UPDATE Products SET quantity = :quantity
                        WHERE id = :pid
                        ''', pid=row.pid, quantity=row.have-row.needed)

                        # increment seller balance
                        getSeller = app.db.execute('''SELECT user_id
                        FROM Products
                        WHERE id = :pid
                        ''', pid=row.pid)

                        seller_uid = int(*getSeller[0])
                        seller = User.get(seller_uid)
                        balance = float(seller.balance) + float(row.needed*row.price)
                        app.db.execute('''UPDATE Users SET balance = :balance
                        WHERE id = :uid
                        ''', uid=seller_uid, balance=balance)
                    
                    # decrement buyer balance
                    buyerBalance = float(user.balance) - float(totalPrice)
                    app.db.execute('''UPDATE Users SET balance = :balance
                    WHERE id = :uid
                    ''', uid=uid, balance=buyerBalance)
                    
                    # delete everything from the user's cart
                    app.db.execute('''DELETE FROM Carts
                    WHERE uid = :uid
                    ''', uid=uid)
                    return render_template('successfulorder.html', oid=oid, totalPrice=totalPrice)

    # load cart html template
    elif request.method == "GET":
        return render_template('cart.html', title='Cart', user=user, cart=cart, totalPrice=totalPrice, quantities=quantities, form=form)
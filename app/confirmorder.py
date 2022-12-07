from flask import current_app as app
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_login import current_user
from .models.user import User, BadUpdateException
from .cart import Cart, CartPrice
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
bp = Blueprint('confirmorder', __name__)

# the Coupon class allows a coupon to be typed into a field
class Coupon(FlaskForm):
    coupon = StringField('Promotional Coupon Code:', validators=[])

@bp.route('/confirmorder', methods=['GET', 'POST'])
@bp.route('/confirmorder/<action>/<uid>', methods=['GET', 'POST'])
def confirmorder(action=None, uid=None):
    uid = current_user.id # loads the user's id
    user = User.get(current_user.id) # gets the user information
    cart = Cart.get_all_by_uid(current_user.id) # loads the user's cart
    totalPrice = CartPrice.getPrice(current_user.id) # loads the total price of the user's cart
    discount = 0 # variable to keep track of if a coupon was used
    couponDict = {'HOLIDAYS': 0.8, 'WINTER22': 0.78, '20OFF': 0.8, 'HALFOFF': 0.5} # tracks the available coupons
    percDict = {'HOLIDAYS': '20%', 'WINTER22': '22%', '20OFF': '20%', 'HALFOFF': '50%'}

    form = Coupon() # type in coupons
    
    # the posting methods allow for coupons to be applied and carts to be purchased
    if request.method == "POST":
        # apply a coupon
        if action == 'coupon':
            if form.validate_on_submit:
                code = form.coupon.data.strip() # gets what was typed into the field
                
                # if a coupon was already used, you cannot use another coupon
                if discount == 1:
                    flash('You already have a coupon applied!')
                    return redirect(url_for('confirmorder.confirmorder'))

                # if coupon is a valid coupon
                elif code in couponDict:
                    discount = 1 # set variable so you can't use another coupon
                    multiplier = couponDict[code]
                    discountedPrice = '%.2f' % (multiplier * float(totalPrice))
                    flash('You saved {}!'.format(percDict[code]))
                    return render_template('confirmorder.html', title='Cart', user=user, cart=cart, totalPrice=discountedPrice, form=form)
                
                # coupon is invalid
                else:
                    flash('Invalid coupon code!')
                    return redirect(url_for('confirmorder.confirmorder'))

        # allows users to order what is in their cart
        if action == 'confirm':
            # if nothing is in the cart, nothing happens
            if len(cart) == 0:
                flash('Add items to your cart before ordering!')
                return redirect(url_for('confirmorder.confirmorder'))
            
            # sees if a discount was applied or not
            if 'totalPrice' in request.form:
                totalPrice = request.form['totalPrice']
            
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
    return render_template('confirmorder.html', title='Cart', user=user, cart=cart, totalPrice=totalPrice, form=form)
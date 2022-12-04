from flask import current_app as app
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from flask_login import current_user
from .models.user import User, BadUpdateException
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
bp = Blueprint('save', __name__)

# SAVED FOR LATER PAGE:

# the Save class has all the components to load the saved for later feature on our ecommerce site
class Save:
    def __init__(self, uid, pid, name, price, time):
        self.uid = uid
        self.pid = pid
        self.name = name
        self.price = price
        self.time = time
    
    # this method gets the items saved for later for a specific user
    @staticmethod
    def get_by_uid(uid):
        rows = app.db.execute('''
SELECT uid, pid, name, price, time
FROM Saved, Products
WHERE uid = :uid
AND Saved.pid = Products.id
ORDER BY time DESC
''', uid=uid)
        return [Save(*row) for row in rows]

# save loads all the relevant information from the database
@bp.route('/save', methods=['GET', 'POST'])
@bp.route('/save/<action>/<uid>/<pid>', methods=['GET', 'POST'])
def save(action=None, uid=None, pid=None):
    user = User.get(current_user.id) # gets the user information
    saved = Save.get_by_uid(current_user.id) # gets the items saved for later

    # the posting methods allow for customizability of the saved for later feature
    # including adding items and deleting items
    if request.method == "POST":
        # allows users to add items back to cart
        if action == 'add':
            # delete the item from saved for later table
            app.db.execute('''DELETE FROM Saved
            WHERE uid = :uid AND pid = :pid
            ''', uid=uid, pid=pid)

            # add item to cart
            app.db.execute('''INSERT INTO Carts (uid, pid, quantity, time_added_to_cart)
            VALUES (:uid, :pid, 1, current_timestamp(0))
            RETURNING id
            ''', uid=uid, pid=pid)
            return redirect(url_for('save.save'))
        
        # allows users to delete items from saved for later list
        if action == 'delete':
            app.db.execute('''DELETE FROM Saved
            WHERE uid = :uid AND pid = :pid
            ''', uid=uid, pid=pid)
            return redirect(url_for('save.save'))

    # load saved html template
    return render_template('saved.html', title='Saved', user=user, saved=saved)

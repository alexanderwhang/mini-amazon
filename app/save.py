from flask import current_app as app
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from flask_login import current_user
from .models.user import User, BadUpdateException
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
bp = Blueprint('save', __name__)

class Save:
    def __init__(self, uid, pid, name, price, time):
        self.uid = uid
        self.pid = pid
        self.name = name
        self.price = price
        self.time = time
    
    @staticmethod
    def get_by_uid(uid):
        rows = app.db.execute('''
SELECT uid, pid, name, price, time
FROM Saved, Products
WHERE uid = :uid
AND Saved.pid = Products.id
ORDER BY time DESC
''',
                              uid=uid)
        return [Save(*row) for row in rows]

@bp.route('/save', methods=['GET', 'POST'])
@bp.route('/save/<action>/<uid>/<pid>', methods=['GET', 'POST'])
def save(action=None, uid=None, pid=None):
    user = User.get(current_user.id)
    saved = Save.get_by_uid(current_user.id)

    if request.method == "POST":
        if action == 'add':
            app.db.execute('''DELETE FROM Saved
            WHERE uid = :uid AND pid = :pid''', uid=uid, pid=pid)

            app.db.execute('''INSERT INTO Carts (uid, pid, quantity, time_added_to_cart)
            VALUES (:uid, :pid, 1, current_timestamp(0))
            RETURNING id''', uid=uid, pid=pid)

            return redirect(url_for('save.save'))
        
        if action == 'delete':
            app.db.execute('''DELETE FROM Saved
            WHERE uid = :uid AND pid = :pid''', uid=uid, pid=pid)
            return redirect(url_for('save.save'))

    return render_template('saved.html', title='Saved', user=user, saved=saved)
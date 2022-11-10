from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User, BadUpdateException


from flask import Blueprint
bp = Blueprint('inventory', __name__)


@bp.route('/seller', methods=['GET', 'POST'])
def seller():
    # get all available products for sale:
    inventory = Inventory.get_all_inventories_by_user(current_user.id)
    fulfillment = Fulfillment.get_all_fulfillment_by_user(current_user.id)
    # find the products current user has bought:
    #if current_user.is_authenticated:
    #    orders = Purchase.get_all_purchases_by_user(Purchase.user_email_to_id(current_user.email))
        # print(current_user.email)

    # render the page by adding information to the index.html file
    return render_template('inventory.html',
                           purchase_history=orders,
                           all_products = inventory)
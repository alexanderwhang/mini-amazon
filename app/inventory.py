from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User, BadUpdateException
from .models.product import Product, BadUpdateException
from .models.seller import Inventory, Fulfillment



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
                           purchase_history=fulfillment,
                           all_products = inventory)


class AddInventoryForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    imageurl = StringField('Image url', validators=[DataRequired()])
    quantity = StringField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Register Item')

@bp.route('/addinventory', methods=['GET', 'POST'])
def addinventory():
    form = AddInventoryForm()
    if form.validate_on_submit():
        try:
            ret = Product.add_product(current_user.id,
                        form.name.data.strip(), 
                        form.category.data.strip(),
                        form.description.data.strip(),
                        form.price.data.strip(),
                        form.imageurl.data.strip(),
                        form.quantity.data.strip()
                        )
            if ret is not None:
                flash('User Information Updated')
            return redirect(url_for('inventory.seller'))
        except BadUpdateException as e:
            flash(e.toString())
    return render_template('addinventory.html', form=form)

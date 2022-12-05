from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from flask_login import login_user, logout_user, current_user
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.product import Product, BadUpdateException
from .models.review import Review


from flask import Blueprint
bp = Blueprint('searchproduct', __name__)

class FindProductBySKU(FlaskForm):
    productSKU = StringField('Search for a Product by SKU', validators=[])
    submitSKU = SubmitField('Search')

class FindProductByName(FlaskForm):
    productName = StringField('Search for a Product by Name', validators=[])
    submitName = SubmitField('Search')

@bp.route('/searchbySKU', methods=['GET', 'POST'])
def searchbySKU():
    SKUForm = FindProductBySKU()
    product = None
    sku = request.args.get('sku', None)
    if current_user.is_authenticated:
        user_id = Review.user_email_to_id(current_user.email)
    user_review_exists = None
    if sku != None:
        product = Product.get_SKU(sku)
        if product is None:
            flash(f"Product with SKU {SKUForm.productSKU.data.strip()} not found")
    else:    
        if SKUForm.validate_on_submit():
            if len(SKUForm.productSKU.data.strip()) > 0:
                product = Product.get_SKU(SKUForm.productSKU.data.strip())
                if current_user.is_authenticated:
                    user_review_exists = Review.review_exists_check(user_id, SKUForm.productSKU.data.strip())
                print(user_review_exists)
                if product is None:
                    flash(f"Product with SKU {SKUForm.productSKU.data.strip()} not found")

    return render_template('searchproduct.html', 
                        title='SearchSKU', 
                        products=product,
                        form=SKUForm,
                        user_review_exists=user_review_exists)

@bp.route('/searchbyName', methods=['GET', 'POST'])
def searchbyName():
    NameForm = FindProductByName()
    listofproducts = None
    if current_user.is_authenticated:
        user_id = Review.user_email_to_id(current_user.email)
    user_review_exists = None
    if NameForm.validate_on_submit():
        if len(NameForm.productName.data.strip()) > 0:
            listofproducts = Product.get_Name(NameForm.productName.data.strip())
            if listofproducts is None:
                flash(f"No products containing '{NameForm.productName.data.strip()}' found.")

    return render_template('searchproductname.html', 
                        title='SearchName', 
                        listofproducts=listofproducts,
                        form=NameForm,
                        user_review_exists=user_review_exists)
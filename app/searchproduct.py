from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.product import Product, BadUpdateException


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
    if SKUForm.validate_on_submit():
        if len(SKUForm.productSKU.data.strip()) > 0:
            product = Product.get_SKU(SKUForm.productSKU.data.strip())
            print(product)
            if product is None:
                flash(f"Product with SKU {SKUForm.productSKU.data.strip()} not found")

    return render_template('searchproduct.html', 
                        title='SearchSKU', 
                        products=product,
                        form=SKUForm)
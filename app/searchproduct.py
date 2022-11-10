from flask import render_template, redirect, url_for, flash, request
from numpy import product
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
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
    if product is None:
                flash("Product not found")
    return render_template('searchproduct.html', 
                        title='SearchSKU', 
                        product=product,
                        form=SKUForm)
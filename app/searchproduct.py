from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from flask_login import login_user, logout_user, current_user
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User
from .models.product import Product, BadUpdateException
from .models.review import Review


from flask import Blueprint
bp = Blueprint('searchproduct', __name__)

class FindProductBySKU(FlaskForm):
    productSKU = StringField('Search for a Product by SKU', validators=[])
    submitSKU = SubmitField('Search')

class FindProductByName(FlaskForm):
    productName = StringField('Keyword Search', validators=[])
    submitName = SubmitField('Search')

@bp.route('/searchbySKU', methods=['GET', 'POST'])
def searchbySKU():
    SKUForm = FindProductBySKU()
    product = None
    number_of_ratings = None
    sku = request.args.get('sku', None)
    uid = request.args.get('uid', None)
    if uid != None:
        Product.addCart(sku, uid)
    if current_user.is_authenticated:
        user_id = Review.user_email_to_id(current_user.email)
    user_review_exists = None
    user_review = None
    seller = None
    if sku != None:
        Review.update_product_ratings(sku) # Update product rating in database before displaying
        number_of_ratings = Review.count_num_ratings(sku)
        product = Product.get_SKU(sku)
        if current_user.is_authenticated:
            user_review_exists = Review.review_exists_check(user_id, product[0].product_id)
            user_review = Review.get_review(user_id, product[0].product_id)
        if product is None:
            flash(f"Product with SKU {SKUForm.productSKU.data.strip()} not found")
    else:    
        if SKUForm.validate_on_submit():
            if len(SKUForm.productSKU.data.strip()) > 0:
                number_of_ratings = Review.count_num_ratings(SKUForm.productSKU.data.strip())
                Review.update_product_ratings(SKUForm.productSKU.data.strip()) # Update product rating in database before displaying
                product = Product.get_SKU(SKUForm.productSKU.data.strip())
                if current_user.is_authenticated:
                    user_review_exists = Review.review_exists_check(user_id, SKUForm.productSKU.data.strip())
                    user_review = Review.get_review(user_id, SKUForm.productSKU.data.strip())
                if product is None:
                    flash(f"Product with SKU {SKUForm.productSKU.data.strip()} not found")
    if product is not None:
        seller = User.get(product[0].user_id)

    return render_template('searchproduct.html', 
                        title='SearchSKU', 
                        products=product,
                        form=SKUForm,
                        user_review_exists=user_review_exists,
                        user_review = user_review,
                        number_of_ratings = number_of_ratings,
                        seller = seller)

@bp.route('/searchbyName', methods=['GET', 'POST'])
def searchbyName():
    NameForm = FindProductByName()
    listofproducts = None
    cat = request.args.get('cat', None)
    if cat != None:
        listofproducts = Product.getbyCat(cat)
        if listofproducts is not None:
            for product in listofproducts:
                Review.update_product_ratings(product.product_id) # Update product rating in database before displaying
        listofproducts = Product.getbyCat(cat)
    else:
        if current_user.is_authenticated:
            user_id = Review.user_email_to_id(current_user.email)
        if NameForm.validate_on_submit():
            if len(NameForm.productName.data.strip()) > 0:
                listofproducts = Product.get_Name(NameForm.productName.data.strip())
                if listofproducts is None:
                    flash(f"No products containing '{NameForm.productName.data.strip()}' found.")
                else:
                    for product in listofproducts:
                        Review.update_product_ratings(product.product_id) # Update product rating in database before displaying
                listofproducts = Product.get_Name(NameForm.productName.data.strip())

    return render_template('searchproductname.html', 
                        title='SearchName', 
                        listofproducts=listofproducts,
                        form=NameForm)

@bp.route('/browse', methods=['GET', 'POST'])
def browse():
    listofcategories = Product.get_Cat()

    return render_template('browse.html', 
                        title='Browse', 
                        listofcategories=listofcategories)
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User, BadUpdateException
from .models.product import Product
from .models.purchase import Purchase
from .models.sellerreview import SellerReview
from .models.review import Review

from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.address.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

class EditProfileForm(FlaskForm):
    newEmail = StringField('New Email', validators=[])
    newPassword = PasswordField('New Password', validators=[])
    newAddress = StringField('New Address', validators=[])
    newFirstName = StringField('New First Name', validators=[])
    newLastName = StringField('New Last Name', validators=[])
    newBalance = StringField('New Balance', validators=[])
    passwordConfirmation = PasswordField('Enter Password to Confirm', validators=[DataRequired()])
    submit = SubmitField('Update')

@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user = User.get(current_user.id)
    form = EditProfileForm()

    if form.validate_on_submit():
        try:
            ret = User.updateUser(user.id, 
                        form.newEmail.data.strip(), 
                        form.newPassword.data,
                        form.newAddress.data.strip(),
                        form.newFirstName.data.strip(),
                        form.newLastName.data.strip(),
                        form.newBalance.data.strip(),
                        form.passwordConfirmation.data,
                        )
        
            if ret is not None:
                flash('User Information Updated')
                user = ret
            return redirect(url_for('users.profile'))
        except BadUpdateException as e:
            flash(e.toString())
    return render_template('profile.html', title='Edit Profile', user=user, form=form)

class FindUserForm(FlaskForm):
    userId = StringField('Search a User ID', validators=[])
    submit = SubmitField('Search')
    
def getReviewsOfSeller(current_user_id, sellerid):
    if current_user_id is None:
        reviewForSellerExists = False
    else:
        num_seller_reviews = SellerReview.review_exists_check(current_user_id, sellerid)
        reviewForSellerExists = True if num_seller_reviews > 0 else False

    sellerReviews = SellerReview.get_all_seller_reviews(sellerid)
    return sellerReviews, reviewForSellerExists
 
def getProductsOfSeller(sellerid):
    soldProducts = Product.get_itemsSoldByUser(sellerid)
    for product in soldProducts:
        Review.update_product_ratings(product.product_id)
    return soldProducts
   
def getSellerRatings(isSeller, sellerReviews):
    sellerNumReviews = 0
    sellerAvgRating = 0
    if len(sellerReviews) == 0:
        sellerAvgRating = None
    elif isSeller:
        for review in sellerReviews:
            sellerAvgRating = review.review_rating
            sellerNumReviews = sellerNumReviews + 1
        sellerAvgRating = sellerAvgRating / sellerNumReviews
    return sellerAvgRating, sellerNumReviews

def hasProductPurchasedFromSeller(user_id, sellerid):
    return SellerReview.can_user_review_seller(user_id, sellerid)
     
@bp.route('/user', methods=['GET', 'POST'])
def user():
    form = FindUserForm()
    user = None
    isSeller = False
    soldProducts = []
    sellerReviews = None
    sellerReviewExists = False
    sellerReviews = [] 
    reviewForSellerExists = False
    sellerAvgRating = None 
    sellerNumReviews = 0
    canReviewThisSeller = False
    reviews = []

    passedin_sellerid = request.args.get('sellerid', default=None, type=None)

    if passedin_sellerid is not None and current_user.is_authenticated:
        # form = None
        user = User.get(passedin_sellerid)
        if user is None:
            flash(f"User {form.userId.data.strip()} not found")
        else:
            sellerReviews, reviewForSellerExists = getReviewsOfSeller(current_user.id, user.id)
            soldProducts = getProductsOfSeller(user.id)
            isSeller = True if len(soldProducts) > 0 else False 
            sellerAvgRating, sellerNumReviews =  getSellerRatings(isSeller, sellerReviews)
            canReviewThisSeller = True
        return render_template('user.html', 
            title='User', 
            isSeller = isSeller, #if true, displays soldProducts
            soldProducts=soldProducts,
            user=user, 
            form=None,
            sellerReviews = sellerReviews,
            sellerReviewExists = reviewForSellerExists,
            sellerAvgRating = sellerAvgRating,
            sellerNumReviews = sellerNumReviews,
            canReviewThisSeller = canReviewThisSeller)
             

    if form.validate_on_submit():
        if len(form.userId.data.strip()) > 0:
            user = User.get(form.userId.data.strip())
            if user is None:
                flash(f"User {form.userId.data.strip()} not found")
                return render_template('user.html', 
                    title='User', 
                    isSeller = isSeller, #if true, displays soldProducts
                    soldProducts=soldProducts,
                    user=user, 
                    form=form,
                    sellerReviews = sellerReviews,
                    sellerReviewExists = reviewForSellerExists,
                    sellerAvgRating = sellerAvgRating,
                    sellerNumReviews = sellerNumReviews,
                    canReviewThisSeller = canReviewThisSeller)
            else:
                soldProducts = getProductsOfSeller(user.id)
                isSeller = True if len(soldProducts) > 0 else False 
        if current_user.is_authenticated:
            sellerReviews, reviewForSellerExists = getReviewsOfSeller(current_user.id, user.id)
            canReviewThisSeller = hasProductPurchasedFromSeller(current_user.id, user.id)
        else:
            sellerReviews, reviewForSellerExists = getReviewsOfSeller(None, user.id)

        sellerAvgRating, sellerNumReviews =  getSellerRatings(isSeller, sellerReviews)

    if user is None:
        return render_template('user.html', title='User', form=form)

    return render_template('user.html', 
                title='User', 
                isSeller = isSeller, #if true, displays soldProducts
                soldProducts=soldProducts,
                user=user, 
                form=form,
                sellerReviews = sellerReviews,
                sellerReviewExists = reviewForSellerExists,
                sellerAvgRating = sellerAvgRating,
                sellerNumReviews = sellerNumReviews,
                canReviewThisSeller = canReviewThisSeller)


class SearchPurchaseForm(FlaskForm):
    keyword = StringField('Search Past Purchases', validators=[])
    submit = SubmitField('Search')

@bp.route('/purchasehistory', methods=['GET', 'POST'])
@bp.route('/purchasehistory/<action>', methods=['GET', 'POST'])
def purchasehistory(action=None):
    user = User.get(current_user.id)
    datefilter = "all"
    form = SearchPurchaseForm()

    if request.method == "POST":
        if action=="filterdate":
            if 'dateFilter' in request.form:
                datefilter=request.form['dateFilter']
                purchases = Purchase.get_all_purchases_by_user(current_user.id, datefilter)
                return render_template('userpurchases.html', 
                            title='User Purchases',
                            currDatefilter=datefilter,
                            purchase_history=purchases,
                            form=form)

    if form.validate_on_submit():
        if len(form.keyword.data.strip()) > 0:
            purchases = Purchase.get_all_purchases_by_user(current_user.id, datefilter, form.keyword.data.strip())
            print(purchases)
            if len(purchases) == 0:
                flash(f"No Items Found")
            return render_template('userpurchases.html', 
                        title='User Purchases',
                        currDatefilter=datefilter,
                        purchase_history=purchases,
                        form=form)

    purchases = Purchase.get_all_purchases_by_user(current_user.id,datefilter)
    return render_template('userpurchases.html', 
                        title='User Purchases',
                        currDatefilter=datefilter,
                        purchase_history=purchases,
                        form=form)

   
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

# form for logging in
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

#login page
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: #if user already logged in, redirect to home page
        return redirect(url_for('index.index'))

    #User submits email and PW
    form = LoginForm()
    if form.validate_on_submit(): 
        user = User.get_by_auth(form.email.data, form.password.data) #see if user exists with given email + PW
        
        #Incorrect Login. Loads login page again
        if user is None: 
            flash('Invalid email or password')
            return redirect(url_for('users.login')) 
        
        #Correct Login. Goes to home page 
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

#form for creating a new account
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

    #checks that email isn't already used
    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

#page to create a new account
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: #if user is already logged in, redirect to home page
        return redirect(url_for('index.index'))
    
    #Try to create a new account. upon success redirect to login page.
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.address.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
        else:
            # If registration fails, flash a message
            flash('Registration failed. Try again')
    return render_template('register.html', title='Register', form=form)

#action when user clicks logout button. returns to home page
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

#form for editing a users information
class EditProfileForm(FlaskForm):
    newEmail = StringField('New Email', validators=[])
    newPassword = PasswordField('New Password', validators=[])
    newAddress = StringField('New Address', validators=[])
    newFirstName = StringField('New First Name', validators=[])
    newLastName = StringField('New Last Name', validators=[])
    newBalance = StringField('New Balance', validators=[])
    passwordConfirmation = PasswordField('Enter Password to Confirm', validators=[DataRequired()])
    submit = SubmitField('Update')

#page to see and change a users personal information
@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not current_user.is_authenticated: #if user is not logged in, render nothing
        return render_template('profile.html', title='Edit Profile')

    user = User.get(current_user.id)
    form = EditProfileForm()
    if form.validate_on_submit():
        try: #try to update user information.
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

        #If input is not valid, show error message explaining why
        except BadUpdateException as e:  
            flash(e.toString())
    return render_template('profile.html', title='Edit Profile', user=user, form=form)

#form for searching for users
class FindUserForm(FlaskForm):
    userId = StringField('Search a User ID', validators=[])
    submit = SubmitField('Search')
    
'''
Helper function for the user_search page. returns reviews for a seller
Inputs
    current_user_id: str
    sellerid: str
Returns
    sellerReviews: list
        all reviews for the seller
    reviewForSellerExists: boolean 
        if the current_user_id has written a review for the seller
'''
def getReviewsOfSeller(current_user_id, sellerid):
    if current_user_id is None: 
        #case for when no user is logged in.
        reviewForSellerExists = False
    else:
        num_seller_reviews = SellerReview.review_exists_check(current_user_id, sellerid)
        reviewForSellerExists = True if num_seller_reviews > 0 else False

    sellerReviews = SellerReview.get_all_seller_reviews(sellerid)
    return sellerReviews, reviewForSellerExists

'''
Helper function for the user_search page. returns products sold by the seller
Inputs
    sellerid: str
Returns
    soldProducts: list
        all products sold by the seller
'''
def getProductsOfSeller(sellerid):
    soldProducts = Product.get_itemsSoldByUser(sellerid)
    for product in soldProducts:
        Review.update_product_ratings(product.product_id)
    return soldProducts
   
'''
Helper function for the user_search page. returns avg_rating and num_reviews for a seller
Inputs
    isSeller: boolean
    sellerReviews: list
        list of all reviews for the seller
Returns
    sellerAvgRating: int or None
        average rating between 1 and 5.
        if the seller has no reviews, the avg_rating is None
    sellerNumReviews: int
        size of sellerReviews
'''
def getSellerRatings(sellerReviews):
    sellerNumReviews = 0
    sellerAvgRating = 0
    if len(sellerReviews) == 0: 
        #case for when no reviews exist. Avg is None, num is zero
        sellerAvgRating = None
    else: 
        for review in sellerReviews:
            sellerAvgRating = review.review_rating
            sellerNumReviews = sellerNumReviews + 1
        sellerAvgRating = sellerAvgRating / sellerNumReviews
    return sellerAvgRating, sellerNumReviews

'''
Helper function for the user_search page. returns if the user can review a seller
Inputs
    user_id: str
    sellerid: str
Returns
    boolean
        if the user already has written a review, they are ineligible to write another
        
'''
def hasProductPurchasedFromSeller(user_id, sellerid):
    return SellerReview.can_user_review_seller(user_id, sellerid)
     
#page for looking up a user's information 
@bp.route('/user', methods=['GET', 'POST'])
def user():
    form = FindUserForm()
    user = None #user of interest
    isSeller = False #if true, displays soldProducts
    soldProducts = [] #list of sold products by the target user
    sellerReviews = [] #list of reviews written about the target user
    reviewForSellerExists = False #boolean of if the current_user has written a review for the target user
    sellerAvgRating = None #avg rating for the target user
    sellerNumReviews = 0 #number of reviews written about the target user
    canReviewThisSeller = False #boolean of if the current_user can write a review for the target user
    reviews = [] #list of reviews written about the target user

    #case when users are redirected from other pages in regards to looking up a seller's information
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
            sellerAvgRating, sellerNumReviews =  getSellerRatings(sellerReviews)
            canReviewThisSeller = True
        return render_template('user.html', 
            title='User', 
            isSeller = isSeller, 
            soldProducts=soldProducts,
            user=user, 
            form=None,
            sellerReviews = sellerReviews,
            sellerReviewExists = reviewForSellerExists,
            sellerAvgRating = sellerAvgRating,
            sellerNumReviews = sellerNumReviews,
            canReviewThisSeller = canReviewThisSeller)
             
    #case when user is searching up a user
    if form.validate_on_submit():
        if len(form.userId.data.strip()) > 0:
            try: 
                user = User.get(form.userId.data.strip())
            except:
                user = None
            if user is None:
                flash(f"User {form.userId.data.strip()} not found")
                return render_template('user.html', 
                    title='User', 
                    isSeller = isSeller, #if true, displays soldProducts
                    soldProducts=soldProducts,
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
            #if the user is logged in, see if the user has written reviews for the user
            sellerReviews, reviewForSellerExists = getReviewsOfSeller(current_user.id, user.id)
            canReviewThisSeller = hasProductPurchasedFromSeller(current_user.id, user.id)
        else:
            #else just show reviews for the seller
            sellerReviews, reviewForSellerExists = getReviewsOfSeller(None, user.id)

        #calc avg and num review
        sellerAvgRating, sellerNumReviews =  getSellerRatings(sellerReviews)

    # if no user is found, display just the search bar
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

#form for searching a users purchase history by product name
class SearchPurchaseForm(FlaskForm):
    keyword = StringField('Search Past Purchases', validators=[])
    submit = SubmitField('Search')

#page for displaying a users purchase history
@bp.route('/purchasehistory', methods=['GET', 'POST'])
@bp.route('/purchasehistory/<action>', methods=['GET', 'POST'])
def purchasehistory(action=None):
    #by default, display all purchases and sort by time purchased
    datefilter="all"
    sortby="time"
    form = SearchPurchaseForm()

    #if user is not logged in, display nothing
    if not current_user.is_authenticated:
        return render_template('purchasehistory.html', 
                        title='User Purchases',
                        currDatefilter=datefilter,
                        currSortBy=sortby,
                        purchase_history=[],
                        form=form)

    #if user changes the datefilter type or sortby field, update the page to display filtered/sorted purchases
    user = User.get(current_user.id)
    if request.method == "POST":
        if action=="filterSort":
            if 'dateFilter' in request.form:
                datefilter=request.form['dateFilter']
            if 'sortby' in request.form:
                sortby=request.form['sortby']
            purchases = Purchase.get_all_purchases_by_user(current_user.id, datefilter, sortby)
            return render_template('purchasehistory.html', 
                        title='User Purchases',
                        currDatefilter=datefilter,
                        currSortBy=sortby,
                        purchase_history=purchases,
                        form=form)

    #if the user searches for a product by name in their purchase history
    if form.validate_on_submit():
        if len(form.keyword.data.strip()) > 0:
            purchases = Purchase.get_all_purchases_by_user(current_user.id, datefilter, sortby, form.keyword.data.strip())
            if len(purchases) == 0:
                flash(f"No Items Found")
            return render_template('purchasehistory.html', 
                        title='User Purchases',
                        currDatefilter=datefilter,
                        currSortBy=sortby,
                        purchase_history=purchases,
                        form=form)

    #default display of a users purchase history: all items, sorted by time purchased
    purchases = Purchase.get_all_purchases_by_user(current_user.id,datefilter, sortby)
    return render_template('purchasehistory.html', 
                        title='User Purchases',
                        currDatefilter=datefilter,
                        currSortBy=sortby,
                        purchase_history=purchases,
                        form=form)

   
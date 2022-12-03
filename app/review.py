from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from flask_login import login_user, logout_user, current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange

from .models.review import Review
from .models.user import User


from flask import Blueprint
bp = Blueprint('review', __name__)

class EditReview(FlaskForm):
    newReview = StringField('Enter New Review', validators=[DataRequired()])
    newRating = DecimalField('Enter New Rating', validators=[DataRequired(),  NumberRange(min=1, max=5)])
    submitReview = SubmitField('Submit')

class AddReview(FlaskForm):
    newReview = StringField('Enter New Review', validators=[])
    newRating = DecimalField('Enter New Rating', validators=[DataRequired(),  NumberRange(min=1, max=5)])
    submitReview = SubmitField('Submit')

@bp.route('/editreview', methods=['GET', 'POST'])
def editreview():
    editReviewForm = EditReview()
    # review_id = request.args.get('review_id', None)
    product_id = request.args.get('product_id', None)
    user_id = Review.user_email_to_id(current_user.email)
    if editReviewForm.validate_on_submit():
        if len(editReviewForm.newReview.data.strip()) > 0:
            Review.edit_review(product_id, user_id, editReviewForm.newReview.data.strip(),editReviewForm.newRating.data)
            return redirect(url_for('index.index'))
    return render_template('editreview.html', 
                        form = editReviewForm)

@bp.route('/addreview', methods=['GET', 'POST'])
def addreview():
    addReviewForm = AddReview()
    product_id = request.args.get('product_id', None)
    user_id = Review.user_email_to_id(current_user.email)
    if addReviewForm.validate_on_submit():
        if len(addReviewForm.newReview.data.strip()) > 0:
            Review.add_review(product_id, user_id, addReviewForm.newReview.data.strip(),addReviewForm.newRating.data)
            return redirect(url_for('index.index'))
    return render_template('addreview.html', 
                        form = addReviewForm)

@bp.route('/showproductreviews', methods=['GET', 'POST'])
def showproductreviews():
    product_id = request.args.get('product_id', None)
    allReviews = Review.get_all_by_pid(product_id)
    if current_user.is_authenticated:
        print(current_user.id)
        return render_template('productreviewlist.html',
                        all_product_reviews = allReviews,
                        curruserid=current_user.id)
    else:
        return render_template('productreviewlist.html',
                        all_product_reviews = allReviews)
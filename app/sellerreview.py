from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from flask_login import login_user, logout_user, current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange

from .models.sellerreview import SellerReview
from .models.review import Review
from .models.user import User


from flask import Blueprint
bp = Blueprint('sellerreview', __name__)

class EditSellerReview(FlaskForm):
    newReview = StringField('Enter New Review', validators=[DataRequired()])
    newRating = DecimalField('Enter New Rating', validators=[DataRequired(),  NumberRange(min=1, max=5)])
    submitReview = SubmitField('Submit')

class AddSellerReview(FlaskForm):
    newReview = StringField('Enter New Review', validators=[])
    newRating = DecimalField('Enter New Rating', validators=[DataRequired(),  NumberRange(min=1, max=5)])
    submitReview = SubmitField('Submit')

class DeleteSellerReview(FlaskForm):
    deleteReview = SubmitField('Delete')
    cancelDeleteReview = SubmitField('Cancel')
    

@bp.route('/editsellerreview', methods=['GET', 'POST'])
def editsellerreview():
    editSellerReviewForm = EditSellerReview()
    sellerid = request.args.get('sellerid', None)
    user_id = Review.user_email_to_id(current_user.email)
    if editSellerReviewForm.validate_on_submit():
        if len(editSellerReviewForm.newReview.data.strip()) > 0:
            SellerReview.edit_seller_review(user_id, sellerid, editSellerReviewForm.newReview.data.strip(),editSellerReviewForm.newRating.data)
            return redirect(url_for('index.index'))
    return render_template('editsellerreview.html', 
                        form = editSellerReviewForm)

@bp.route('/addsellerreview', methods=['GET', 'POST'])
def addsellerreview():
    addSellerReviewForm = AddSellerReview()
    sellerid = request.args.get('sellerid', None)
    user_id = Review.user_email_to_id(current_user.email)
    if addSellerReviewForm.validate_on_submit():
        if len(addSellerReviewForm.newReview.data.strip()) > 0:
            SellerReview.add_seller_review(user_id, sellerid, addSellerReviewForm.newReview.data.strip(),addSellerReviewForm.newRating.data)
            # Review.update_product_ratings(product_id)
            return redirect(url_for('index.index'))
    return render_template('addsellerreview.html', 
                        form = addSellerReviewForm)

@bp.route('/deletesellerreview', methods=['GET', 'POST'])
def deletesellerreview():
    deleteSellerReviewForm = DeleteSellerReview()
    sellerid = request.args.get('sellerid', None)
    user_id = request.args.get('user_id', None)
    if deleteSellerReviewForm.validate_on_submit():
        if deleteSellerReviewForm.cancelDeleteReview.data:  # if cancel button is clicked, the form.cancel.data will be True
            return redirect(url_for('index.index'))
        SellerReview.delete_seller_review(user_id, sellerid)
        return redirect(url_for('index.index'))
    return render_template('deletesellerreview.html', 
                        form = deleteSellerReviewForm)
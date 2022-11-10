from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User, BadUpdateException


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
    submit = SubmitField('Search')

@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user = User.get(current_user.id)
    form = EditProfileForm()

    if form.validate_on_submit():
        try:
            ret = User.updateUser(user.id, 
                        form.newEmail.data.strip(), 
                        form.newPassword.data.strip(),
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
    
@bp.route('/user', methods=['GET', 'POST'])
def user():
    form = FindUserForm()
    user = None
    if form.validate_on_submit():
        if len(form.userId.data.strip()) > 0:
            user = User.get(form.userId.data.strip())
            print(user)
            if user is None:
                flash(f"User {form.userId.data.strip()} not found")

    return render_template('user.html', 
                        title='User', 
                        user=user, 
                        form=form)
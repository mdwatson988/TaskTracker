from app import app, db
from models import Organization, User, OrganizationUserJunction, Task, TaskDetail
from forms import UserRegistrationForm, OrganizationRegistrationForm, AboutForm, LoginForm, OrganizationSelectionForm, GrantAdminForm, TaskCreationForm, TaskAssignmentForm, TaskSelectionForm
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime


#create routes to direct traffic and data to appropriate HTML template
@app.route('/') #landing page route will allow users to browse all available organizations or direct them to login page
def landingPage():  
    organizations = Organization.query.all()
    if not organizations:
        organizations = []
    return render_template('landingPage.html', title='TaskTracker Home Page', organizations=organizations)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: #if user already logged in, redirect to user profile
        flash('You are already logged in')
        return redirect(url_for('landingPage', _external=True, _scheme='HTTPS'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_pw_hash(form.password.data): #if login data is incorrect, inform user and redirect to login page
            flash('Invalid username or password')
            return redirect(url_for('login', _external=True, _scheme='HTTPS'))
        login_user(user, remember=form.rememberMe.data) #if successful: login, inform user, redirect to user task page
        flash('Login successful')
        return redirect(url_for('tasks', username=current_user.username, _external=True, _scheme='HTTPS'))
    return render_template('login.html', title='Sign in to TaskTracker', form=form) #render login html template, pass form

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful')
    return redirect(url_for('landingPage', _external=True, _scheme="HTTPS"))

@app.route('/user_registration', methods=['GET', 'POST'])
def userRegistration():
    if current_user.is_authenticated:
        flash('You are already logged in')
        return redirect(url_for('landingPage', _external=True, _scheme='HTTPS'))
    form = UserRegistrationForm()
    if form.validate_on_submit():
        if form.validate_username(form.username) and form.validate_email(form.email): #ensure username and email are unique
            user = User(username=form.username.data, nameFirst=form.nameFirst.data, nameLast=form.nameLast.data, email=form.email.data, about=form.about.data)
            user.set_pw_hash(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('landingPage', _external=True, _scheme='HTTPS'))
    return render_template('userRegistration.html', title='TaskTracker User Registration', form=form)

@app.route('/users/<username>/profile', methods=['GET', 'POST'])
@login_required #login required doesn't seem to be working correctly, the dynamic variable in url is interfering - current workaround is that only authenticated users see link in nav bar
def userProfile(username):
    if username == "":
        flash('Please log in to view user profiles')
        return redirect(url_for('landingPage', _external=True, _scheme='HTTPS'))
    user = User.query.filter_by(username=username).first()
    if current_user.username == user.username: #if user viewing their own profile, allow update of AboutMe
        form = AboutForm()
        if form.validate_on_submit():
            user.about = form.about.data
            db.session.commit()
            return redirect(url_for('userProfile', username=user.username, _external=True, _scheme="HTTPS"))
    else:
        form = None
    # use junction table to pull up all organization-user relationships then filter for current user
    userOrganizations = db.session.query(User, Organization).filter(OrganizationUserJunction.userId == User.id, OrganizationUserJunction.organizationId == Organization.id).filter(User.id == user.id).all()
    if not userOrganizations:
        userOrganizations = []
    return render_template('userProfile.html', title='TaskTracker User Profile', user=user, form=form, userOrganizations=userOrganizations)

@app.route('/users/browse')
@login_required # must be a registered user to browse other users
def userBrowse():
    users = User.query.all()
    return render_template('userBrowse.html', title='Browse TaskTracker Users', users=users)

@app.route('/organization_registration', methods=['GET', 'POST'])
def organizationRegistration():
    return "Hello orgReg"

@app.route('/organizations/<name>/profile', methods=['GET', 'POST'])
def organizationProfile(name):
    return "Hello orgProfile"

@app.route('/users/<username>/tasks', methods=['GET', 'POST'])
@login_required
def tasks(username):
    return "Hello tasks"
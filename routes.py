from wtforms.validators import ValidationError
from app import app, db
from models import Organization, User, Junction, Task, TaskDetail
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

# routes for user management
@app.route('/users/register', methods=['GET', 'POST'])
def userRegistration():
    if current_user.is_authenticated:
        flash('You are already logged in')
        return redirect(url_for('landingPage', _external=True, _scheme='HTTPS'))
    form = UserRegistrationForm()
    if form.validate_on_submit():
        if form.validateUsername(form.username) and form.validateEmail(form.email): #ensure username and email are unique
            user = User(username=form.username.data, nameFirst=form.nameFirst.data, nameLast=form.nameLast.data, email=form.email.data, about=form.about.data)
            user.set_pw_hash(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login', _external=True, _scheme='HTTPS'))
    return render_template('userRegistration.html', title='TaskTracker User Registration', form=form)

@app.route('/users/<username>/profile', methods=['GET', 'POST'])
@login_required #login required doesn't seem to be working correctly, the dynamic variable in url is interfering - current workaround is that only authenticated users see link in nav bar
def userProfile(username):
    user = User.query.filter_by(username=username).first()
    if current_user.username == user.username: #if user viewing their own profile, allow update of AboutMe
        form = AboutForm()
        if form.validate_on_submit():
            user.about = form.about.data
            db.session.commit()
            return redirect(url_for('userProfile', username=user.username, _external=True, _scheme="HTTPS"))
    else:
        form = None
    # create list of (User object, Org object) tuples for every organzation associated with selected user
    userOrgPairs = db.session.query(User, Organization).filter(Junction.userId == User.id, Junction.organizationId == Organization.id).filter(User.id == user.id).all()
    userOrganizations = [pair[1] for pair in userOrgPairs] # make list of just organizations belonging to selected user
    if not userOrganizations:
        userOrganizations = []
    return render_template('userProfile.html', title=f"{user.username}'s TaskTracker Profile", user=user, form=form, userOrganizations=userOrganizations)


# routes for organization management
@app.route('/users/browse')
@login_required # must be a registered user to browse other users
def userBrowse():
    users = User.query.all()
    return render_template('userBrowse.html', title='Browse TaskTracker Users', users=users)

@app.route('/organizations/register', methods=['GET', 'POST'])
@login_required # must be logged to create organization and be given organization admin rights
def organizationRegistration():
    form = OrganizationRegistrationForm()
    if form.validate_on_submit():
        if form.validateName(form.name): # ensure org name is unique
            org = Organization(name=form.name.data, about=form.about.data, address=form.address.data, contactUserId=current_user.id) # set organization contact as org creator
            db.session.add(org)
            db.session.commit() # commit org so org.id can be used in following processes
            junction = Junction(organizationId = org.id, userId = current_user.id, orgAdmin=True) # make org creator a member of org and give Admin rights
            db.session.add(junction)
            db.session.commit()
            flash('Congratulations, your organization is now registered!')
            return redirect(url_for('landingPage', _external=True, _scheme='HTTPS'))
    return render_template('organizationRegistration.html', title='TaskTracker Organization Registration', form=form)

@app.route('/organizations/browse')
def organizationBrowse():
    organizations = Organization.query.all()
    return render_template('organizationBrowse.html', title='Browse TaskTracker Organizations', organizations=organizations)

@app.route('/organizations/<name>/profile', methods=['GET', 'POST'])
def organizationProfile(name):
    org = Organization.query.filter_by(name=name).first()
    contact = User.query.filter_by(id = org.contactUserId).first()
    current_member = False
    is_admin = False
    form = None
    if current_user.is_authenticated: # potential extra data for authenticated users
        if current_user.id == org.contactUserId: # if user viewing profile is org creator, allow update of About org
            form = AboutForm()
            if form.validate_on_submit():
                org.about = form.about.data
                db.session.commit()
                return redirect(url_for('organizationProfile', name=org.name, _external=True, _scheme="HTTPS"))
        # check if current user is already a member of selected organization for join/leave, list members links, admin rights
        # query for correct junction object and check variables
        userOrgJunction = Junction.query.filter_by(userId = current_user.id, organizationId = org.id).first()
        if userOrgJunction:
            if current_user.id == userOrgJunction.userId:
                current_member = True
            if userOrgJunction.orgAdmin:
                is_admin = True
    return render_template('organizationProfile.html', title=f"{org.name}'s TaskTracker Profile", org=org, contact=contact, form=form, current_member=current_member, is_admin=is_admin)

@app.route('/organizations/<name>/members', methods=['GET', 'POST'])
@login_required
def organizationMembers(name):
    org = Organization.query.filter_by(name=name).first()
    form = None
    # create list of (User object, Org object) tuples for every user in selected org
    userOrgPairs = db.session.query(User, Organization).filter(Junction.organizationId == Organization.id, Junction.userId == User.id).filter(Organization.id == org.id).all()
    members = [pair[0] for pair in userOrgPairs] # make list of only users from userOrgPairs list
    memberAdminList = []
    for member in members:
        memberJunction = Junction.query.filter_by(userId = member.id, organizationId = org.id).first()
        memberAdminList.append((member, memberJunction.orgAdmin)) # create list of (member, orgAdmin boolean) tuples for every member of the org to be used in the template
    currentUserJunction = Junction.query.filter_by(userId = current_user.id, organizationId = org.id).first()
    if currentUserJunction.orgAdmin: # check if user viewing page is an org admin for granting admin rights to other users
        form = GrantAdminForm()
        if form.validate_on_submit():
            try:
                if form.checkUserId(org, form.newAdminUserId.data):
                    newAdmin = User.query.filter_by(id = form.newAdminUserId.data).first()
                    newAdminJunction = Junction.query.filter_by(userId = newAdmin.id, organizationId = org.id).first()
                    newAdminJunction.orgAdmin = True
                    db.session.commit()
                    flash(f'{newAdmin.username} is now an Admin of {org.name}')
                    return redirect(url_for('organizationMembers', name=org.name, _external=True, _scheme="HTTPS"))
            except ValidationError:
                flash('The provided User ID does not belong to a member of your organization')
                return redirect(url_for('organizationMembers', name=org.name, _external=True, _scheme="HTTPS"))
    return render_template('organizationMemebers.html', title=f"{org.name}'s Member List", org=org, memberAdminList=memberAdminList, form=form)

@app.route('/organizations/<name>/join')
@login_required
def organizationJoin(name):
    org = Organization.query.filter_by(name=name).first()
    junction = Junction(organizationId = org.id, userId = current_user.id, orgAdmin=False)
    db.session.add(junction)
    db.session.commit()
    flash(f'Congratulations, you are now a member of {org.name}.')
    return redirect(url_for("organizationProfile", name=org.name, _external=True, _scheme="HTTPS"))

@app.route('/organizations/<name>/leave')
@login_required
def organizationLeave(name):
    org = Organization.query.filter_by(name=name).first()
    if org.contactUserId == current_user.id:
        flash('Sorry, organization creators are not allowed to leave their organization')
        return redirect(url_for("organizationProfile", name=org.name, _external=True, _scheme="HTTPS"))
    junctionToRemove = Junction.query.filter_by(userId = current_user.id, organizationId = org.id).first()
    db.session.delete(junctionToRemove)
    db.session.commit()
    flash(f'You are no longer a member of {org.name}.')
    return redirect(url_for("organizationProfile", name=org.name, _external=True, _scheme="HTTPS"))

@app.route('/tasks/<username>', methods=['GET', 'POST'])
@login_required
def tasks(username):
    return render_template('tasks.html', title='Current TaskTracker Tasks')
from wtforms.validators import ValidationError
from app import app, db
from models import Organization, User, Junction, Task, TaskDetail
from forms import *
from flask import request, abort, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse, urljoin
from datetime import datetime


#create routes to direct traffic and data to appropriate HTML template
@app.route('/') #landing page route will allow users to browse all available organizations or direct them to login page
def landingPage():  
    return render_template('landingPage.html', title='TaskTracker Home Page')

def is_safe_url(target): # function to check if 'next' url is safe for redirect after @login_required prevented user from accessing requested page
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

# The nav bar has links to dynamic URLs that require login. Additional static URLs (ending in '404') were built which work with @login_required decorator for proper redirection to login page.
# However, this prevents proper 'next' URL redirecting to correct page after login. If static URL is in following list, login route adds dynamic <username> to end of 'next' URL to redirect after login.
# List should be updated if additional dynamic URLs are added to Nav Bar. Dynamic URL must end in <username> or additional list must be created and login route updated.
navBar404URLs = ['/users/organizations/', '/users/profile/', '/tasks/']

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
        next = request.args.get('next') # if login happens after @login_required redirect, use next parameter built into login_required to redirect to originally requested page rather than 'tasks' page
        if next in navBar404URLs: # check if next URL is static 404 URL rather than dynamic URL (for dynamic URLs requiring user login but accessible from nav bar)
            next += current_user.username # add username to redirect to approrpriate dynamic URL
        if not is_safe_url(next): # ensure redirect target is safe
            return abort(400)
        return redirect(next or url_for('tasks', username=current_user.username, _external=True, _scheme='HTTPS'))
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
        try:
            if form.validateUsername(form.username.data): # ensure username is unique
                try:
                    if form.validateEmail(form.email.data): # ensure email is unique
                        user = User(username=form.username.data, nameFirst=form.nameFirst.data, nameLast=form.nameLast.data, email=form.email.data, about=form.about.data)
                        user.set_pw_hash(form.password.data)
                        db.session.add(user)
                        db.session.commit()
                        flash('Congratulations, you are now a registered user!')
                        return redirect(url_for('login', _external=True, _scheme='HTTPS'))
                except ValidationError: # give appropriate error message if username or password is not unique
                    form.email.errors.append('Email address is already in use.')
        except ValidationError:
            form.username.errors.append('Username is already in use.')
    return render_template('userRegistration.html', title='TaskTracker User Registration', form=form)

@app.route('/users/profile/<username>', methods=['GET', 'POST'])
@login_required
def userProfile(username):
    user = User.query.filter_by(username=username).first_or_404()
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
    return render_template('userProfile.html', title=f"{user.username}'s TaskTracker Profile", user=user, form=form, userOrganizations=userOrganizations)

@app.route('/users/profile/')
@login_required
def userProfile404(): # static route used by @login_required if non logged in user clicks nav bar link
    pass

@app.route('/users/organizations/<username>')
@login_required
def userOrganizations(username):
    user = User.query.filter_by(username=username).first()
    # create list of (User object, Org object) tuples for every organzation associated with selected user
    userOrgPairs = db.session.query(User, Organization).filter(Junction.userId == User.id, Junction.organizationId == Organization.id).filter(User.id == user.id).all()
    userOrganizations = [pair[1] for pair in userOrgPairs] # make list of just organizations belonging to selected user
    return render_template('userOrganizations.html', title='Your Organization Memberships', userOrganizations=userOrganizations)

@app.route('/users/organizations/')
@login_required
def userOrganizations404(): # static route used by @login_required if non logged in user clicks nav bar link
    pass

@app.route('/users/browse')
def userBrowse():
    users = User.query.all()
    return render_template('userBrowse.html', title='Browse TaskTracker Users', users=users)

# routes for organization management


@app.route('/organizations/register', methods=['GET', 'POST'])
@login_required # must be logged to create organization and be given organization admin rights
def organizationRegistration():
    form = OrganizationRegistrationForm()
    if form.validate_on_submit():
        try:
            if form.validateName(form.name.data): # ensure org name is unique
                org = Organization(name=form.name.data, about=form.about.data, address=form.address.data, contactUserId=current_user.id) # set organization contact as org creator
                db.session.add(org)
                db.session.commit() # commit org so org.id can be used in following processes
                junction = Junction(organizationId = org.id, userId = current_user.id, orgAdmin=True) # make org creator a member of org and give Admin rights
                db.session.add(junction)
                db.session.commit()
                flash('Congratulations, your organization is now registered!')
                return redirect(url_for('landingPage', _external=True, _scheme='HTTPS'))
        except ValidationError:
            form.name.errors.append('Organization name is already in use.')
    return render_template('organizationRegistration.html', title='TaskTracker Organization Registration', form=form)

@app.route('/organizations/browse')
def organizationBrowse():
    organizations = Organization.query.all()
    return render_template('organizationBrowse.html', title='Browse TaskTracker Organizations', organizations=organizations)

@app.route('/organizations/profile/<name>', methods=['GET', 'POST'])
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

@app.route('/organizations/members/<name>', methods=['GET', 'POST'])
@login_required
def organizationMembers(name):
    org = Organization.query.filter_by(name=name).first()
    form = None
    # create list of (User object, Org object) tuples for every user in selected org
    orgMemberPairs = db.session.query(User, Organization).filter(Junction.organizationId == Organization.id, Junction.userId == User.id).filter(Organization.id == org.id).all()
    members = [pair[0] for pair in orgMemberPairs] # make list of only users from orgMemberPairs list
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
                form.newAdminUserId.errors.append('The provided User ID does not match any users in the organization.')
    return render_template('organizationMembers.html', title=f"{org.name}'s Member List", org=org, memberAdminList=memberAdminList, form=form)

@app.route('/organizations/tasks/<name>', methods=['GET', 'POST'])
@login_required
def organizationTasks(name):
    org = Organization.query.filter_by(name=name).first()
    tasks = Task.query.filter_by(organizationId=org.id).all()
    completeTasks = []
    incompleteTasks = []
    for task in tasks:
        if task.taskComplete:
            completeTasks.append(task)
        else:
            incompleteTasks.append(task)
    isAdmin = Junction.query.filter_by(organizationId = org.id, userId = current_user.id).first().orgAdmin # check orgAdmin status for current user and organization
    form = ClearCompletedTasksForm()
    if form.validate_on_submit(): # if org admin chooses to delete completed tasks
        if form.clearTasks.data:
            for task in completeTasks:
                db.session.delete(task)
            db.session.commit()
            flash('Completed tasks have been cleared from the record')
            return redirect(url_for("organizationTasks", name=org.name, _external=True, _scheme="HTTPS"))
        else:
            flash('Please check the "Clear completed tasks" box to confirm completed task deletion')
            return redirect(url_for("organizationTasks", name=org.name, _external=True, _scheme="HTTPS"))
    return render_template('organizationTasks.html', title=f"{org.name}'s Pending Tasks", org=org, completeTasks=completeTasks, incompleteTasks=incompleteTasks, isAdmin=isAdmin, form=form)

@app.route('/organizations/join/<name>')
@login_required
def organizationJoin(name):
    org = Organization.query.filter_by(name=name).first()
    junction = Junction(organizationId = org.id, userId = current_user.id, orgAdmin=False)
    db.session.add(junction)
    db.session.commit()
    flash(f'You are now a member of {org.name}.')
    return redirect(url_for("organizationProfile", name=org.name, _external=True, _scheme="HTTPS"))

@app.route('/organizations/leave/<name>')
@login_required
def organizationLeave(name):
    org = Organization.query.filter_by(name=name).first()
    if org.contactUserId == current_user.id:
        flash('Sorry, organization creators are not allowed to leave their organization')
        return redirect(url_for("organizationProfile", name=org.name, _external=True, _scheme="HTTPS"))
    currentlyAssignedTasks = Task.query.filter_by(organizationId = org.id, assignedToUserId = current_user.id).all()
    if currentlyAssignedTasks: # unassign task and remove task assignor from task details
        for task in currentlyAssignedTasks:
            task.assignedToUserId = None
            task.details.first().assignedByUserId = None
    junctionToRemove = Junction.query.filter_by(userId = current_user.id, organizationId = org.id).first()
    db.session.delete(junctionToRemove)
    db.session.commit()
    flash(f'You are no longer a member of {org.name}. All associated tasks have been unassigned.')
    return redirect(url_for("organizationProfile", name=org.name, _external=True, _scheme="HTTPS"))


# routes for viewing and managing tasks

@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def taskCreation():
    # create list of (user, organization) tuples for every organization associated with current user
    userOrgPairs = db.session.query(User, Organization).filter(Junction.userId == User.id, Junction.organizationId == Organization.id).filter(User.id == current_user.id).all()
    currentUserOrgs = [pair[1] for pair in userOrgPairs] # create list of all organizations in userOrgPairs
    orgChoices = [(org.id, org.name) for org in currentUserOrgs] # create list of (value, label) tuples used by the SelectField for organizationId in form
    form = TaskCreationForm()
    form.organizationId.choices = orgChoices # set choices for organizationId SelectField
    if form.validate_on_submit():
        task = Task(name=form.name.data, organizationId=form.organizationId.data)
        db.session.add(task)
        db.session.commit() # commit task to DB so taskId can be used in TaskDetail
        taskDetail = TaskDetail(taskId = task.id, createdByUserId = current_user.id, notes = form.notes.data)
        if form.assignToMe.data: # if task creator wants task assigned to them, do so and track in taskDetail
            task.assignedToUserId = current_user.id
            taskDetail.assignedByUserId = current_user.id
        db.session.add(taskDetail)
        db.session.commit()
        flash('Task Creation Successful')
        org = Organization.query.filter_by(id = form.organizationId.data).first()
        return redirect(url_for("organizationTasks", name=org.name)) # redirect to task list for selected organization upon form completion
    return render_template('taskCreation.html', title='Create New TaskTracker Task', form=form)

@app.route('/tasks/<username>')
@login_required
def tasks(username):
    if current_user.is_authenticated:
        tasks = User.query.filter_by(username=username).first_or_404().tasks.all()
        return render_template('tasks.html', title='Your TaskTracker Tasks', tasks=tasks)
    else:
        flash('Please login to view your task list')
        return redirect(url_for('login', _external=True, _scheme="HTTPS"))

@app.route('/tasks/')
@login_required
def tasks404(): # static route used by @login_required if non logged in user clicks nav bar link
    pass

@app.route('/tasks/details/<int:taskId>', methods=['GET', 'POST'])
@login_required
def taskDetails(taskId):
    task = Task.query.filter_by(id = taskId).first()
    details = task.details.first()
    assignedTo = User.query.filter_by(id = task.assignedToUserId).first()
    taskCreator = User.query.filter_by(id = details.createdByUserId).first()
    taskAssignor = User.query.filter_by(id = details.assignedByUserId).first()
    userIsOrgAdmin = Junction.query.filter_by(organizationId = task.organizationId, userId = current_user.id).first().orgAdmin
    if userIsOrgAdmin:
        # (user, organization) tuples for every user in the organization
        userOrgPairs = db.session.query(User, Organization).filter(Junction.userId == User.id, Junction.organizationId == Organization.id).filter(Organization.id == task.organizationId).all()
        usersInOrg = [pair[0] for pair in userOrgPairs]
        userChoices = [(user.id, user.username) for user in usersInOrg] # create list of choices for task assignment form seen by organization admins
    else:
        userChoices = [(taskCreator.id, taskCreator.username)] # if task creator is not admin allow them to assign themselves
    assignmentForm = TaskAssignmentForm()
    assignmentForm.userId.choices = userChoices # set user choices for user assignment form
    if assignmentForm.validate_on_submit():
        task.assignedToUserId = assignmentForm.userId.data
        details.assignedByUserId = current_user.id
        db.session.commit()
        flash('Task assignment successful')
        return redirect(url_for("taskDetails", taskId=task.id, _external=True, _scheme="HTTPS"))
    completionForm = TaskCompletionForm()
    if completionForm.validate_on_submit():
        if completionForm.completed.data:
            task.taskComplete = True
            details.dateComplete = datetime.now()
            db.session.commit()
            flash(f'Task marked complete at {details.dateComplete.hour}:{details.dateComplete.minute}')
            return redirect(url_for("taskDetails", taskId=task.id, _external=True, _scheme="HTTPS"))
        else:
            flash('Please check the "Mark task as completed" box to confirm task completion')
            return redirect(url_for("taskDetails", taskId=task.id, _external=True, _scheme="HTTPS"))
    return render_template('taskDetails.html', title=f"{task.name} Details", task=task, details=details, assignedTo=assignedTo, taskCreator=taskCreator, taskAssignor=taskAssignor, assignmentForm=assignmentForm, completionForm=completionForm)


# 404 error handler
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Email, EqualTo, ValidationError
from models import Junction, User, Organization


class UserRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    nameFirst = StringField('First Name', validators=[InputRequired()])
    nameLast = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    password2 = PasswordField('Repeat Password', validators=[InputRequired(), EqualTo('password')])
    about = TextAreaField('About Me')
    submit = SubmitField('Register')

    #Ensure username and email using for registration are unique
    def validateUsername(self, username):
        user = User.query.filter_by(username=username).first()
        if user:
            raise ValidationError()
        else:
            return True

    def validateEmail(self, email):
        email = User.query.filter_by(email=email).first()
        if email:
            raise ValidationError()
        else:
            return True

class OrganizationRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    address = TextAreaField('Address')
    about = TextAreaField('About')
    submit = SubmitField('Create Organization')

    def validateName(self, name):
        name = Organization.query.filter_by(name=name).first()
        if name:
            raise ValidationError()
        else:
            return True

class AboutForm(FlaskForm): #Field for user and organization profile pages to update their about sections
    about = TextAreaField('About', validators=[InputRequired()])
    submit = SubmitField('Update About')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    rememberMe = BooleanField('Remember Me')
    submit = SubmitField('Login')

class GrantAdminForm(FlaskForm):
    newAdminUserId = IntegerField('New Admin User ID', validators=[DataRequired()])
    submit = SubmitField('Grant Organization Admin Rights')

    def checkUserId(self, org, newAdminUserId):
        newAdminUserObject = db.session.query(User, Organization).filter(Junction.userId == User.id, Junction.organizationId == Organization.id).filter(Organization.id == org.id).filter(User.id == newAdminUserId).first()
        if newAdminUserObject:
            return True
        else:
            raise ValidationError()

class TaskCreationForm(FlaskForm):
    name = StringField('Task Name', validators=[InputRequired()])
    notes = TextAreaField('Task Notes')
    organizationId = SelectField('Which organization needs this task completed?', coerce=int, validators=[DataRequired()])
    assignToMe = BooleanField('Assign this task to my task list')
    submit = SubmitField('Create Task')

class OrganizationSelectionForm(FlaskForm): #This form will be used to select appropriate organization for assigning tasks
    organizationId = SelectField('Select Organization', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Select Organization')

class TaskAssignmentForm(FlaskForm):
    userId = SelectField('Select User', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Task')

class TaskCompletionForm(FlaskForm):
    completed = BooleanField('Mark task as completed')
    submit = SubmitField('Complete Task')

class ClearCompletedTasksForm(FlaskForm):
    clearTasks = BooleanField("Clear completed tasks from this organization's records")
    submit = SubmitField('Clear Tasks')
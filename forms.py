from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models import User, Organization


class UserRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    about = TextAreaField('About Me')
    submit = SubmitField('Register')

    #Ensure username and email using for registration are unique
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is already in use')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('Email address is already in use')

class OrganizationCreationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    about = TextAreaField('About')
    submit = SubmitField('Create Organization')

    def validate_name(self, name):
        name = Organization.query.filter_by(name=name.data).first()
        if name is not None:
            raise ValidationError('Organization name is already in use')

class AboutForm(FlaskForm): #Field used to update the about section for users and organizations
    about = TextAreaField('About', validators=[DataRequired()])
    submit = SubmitField('Update')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    rememberMe = BooleanField('Remember Me')
    submit = SubmitField('Login')

class OrganizationSelectionForm(FlaskForm): #This form will be used to select appropriate organization for joining, granting admin rights, creating tasks, assigning tasks, etc
    organizationId = SelectField('Select Organization', coerce=int, validators=DataRequired())
    submit = SubmitField('Select Organization')

class GrantAdminForm(FlaskForm):
    makeAdmin = BooleanField('Grant Admin')
    submit = SubmitField('Grant Selected Users Organization Admin Rights')

class TaskCreationForm(FlaskForm):
    name = StringField('Task Name', validators=DataRequired())
    notes = TextAreaField('Task Notes')
    submit = SubmitField('Create Task')

class TaskSelectionForm(FlaskForm): #used to select task for user assignment
    taskId = SelectField('Task', validators=DataRequired())
    submit = SubmitField('Select Task')

class TaskAssignmentForm(FlaskForm):
    userId = SelectField('Select User', coerce=int, validators=DataRequired())
    submit = SubmitField('Assign Task')
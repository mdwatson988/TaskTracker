from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Email, EqualTo, ValidationError
from models import User, Organization


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
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already in use.')
        else:
            return True

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email address is already in use.')
        else:
            return True
class OrganizationRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    about = TextAreaField('About')
    submit = SubmitField('Create Organization')

    def validate_name(self, name):
        name = Organization.query.filter_by(name=name.data).first()
        if name:
            raise ValidationError('Organization name is already in use.')
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

class OrganizationSelectionForm(FlaskForm): #This form will be used to select appropriate organization for joining, granting admin rights, creating tasks, assigning tasks, etc
    choices = [(org.id, org.name) for org in Organization.query.all()]
    organizationId = SelectField('Select Organization', coerce=int, choices=choices, validators=[DataRequired()])
    submit = SubmitField('Select Organization')

class GrantAdminForm(FlaskForm):
    makeAdmin = BooleanField('Grant Admin')
    submit = SubmitField('Grant Selected Users Organization Admin Rights')

class TaskCreationForm(FlaskForm):
    name = StringField('Task Name', validators=[InputRequired()])
    notes = TextAreaField('Task Notes')
    submit = SubmitField('Create Task')

class TaskSelectionForm(FlaskForm): #used to select task for user assignment
    taskId = SelectField('Task', coerce=int, validators=[DataRequired()]) #need to add choices - appropriate tasks for user depending on creation/admin status
    submit = SubmitField('Select Task')

class TaskAssignmentForm(FlaskForm):
    userId = SelectField('Select User', coerce=int, validators=[DataRequired()]) #need to add choices - approrpiate users depending on creation/organization status
    submit = SubmitField('Assign Task')
from app import db, loginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


#create database models
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(45), index=True, unique=True, nullable=False)
    passwordHash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(45), index=True, unique=True, nullable=False)
    aboutMe = db.Column(db.Text(255), index=True)
    organizations = db.relationship('Organization', secondary='organization_users', back_populates='users', lazy='dynamic') #set relationship to junction table foreign key
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    # User class functions to manage password hashing
    def set_pw_hash(self, password):
        self.passwordHash = generate_password_hash(password)

    def check_pw_hash(self, password):
        return check_password_hash(self.passwordHash, password)

@loginManager.user_loader #load user for login manager
def load_user(id):
    return User.query.get(int(id))

class Organization(db.Model):
    __tablename__ = 'organizations'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(45), index=True, unique=True, nullable=False)
    about = db.Column(db.Text(255), index=True)
    contactUserId = db.Column(db.Integer(), index=True, nullable=False)
    users = db.relationship('User', secondary='organization_users', back_populates='organizations', lazy='dynamic') #set relationship to junction table
    tasks = db.relationship('Task', backref='organization', lazy='dynamic', cascade='all, delete-orphan')

#junction table for user-organization many to many relationship
class OrganizationUser(db.Model):
    __tablename__ = 'organization_users'
    id = db.Column(db.Integer(), primary_key=True)
    organizationAdmin = db.Column(db.Boolean(), default=False, nullable=False, index=True)
    organizationId = db.Column(db.Integer(), db.ForeignKey('organizations.id'), index=True)
    userId = db.Column(db.Integer(), db.ForeignKey('users.id'), index=True)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(45), index=True, nullable=False)
    taskComplete = db.Column(db.Boolean(), default=False, nullable=False, index=True)
    organizationId = db.Column(db.Integer(), db.ForeignKey('organizations.id'), nullable=False, index=True)
    assignedToUserId = db.Column(db.Integer(), db.ForeignKey('users.id'), index=True)
    tasksInfo = db.relationship('TaskDetail', backref='task', lazy='dynamic', cascade='all, delete-orphan')

class TaskDetail(db.Model):
    __tablename__ = 'task_detail'
    taskId = db.Column(db.Integer(), db.ForeignKey('tasks.id'), primary_key=True, index=True)
    createdByUserId = db.Column(db.Integer(), nullable=False, index=True)
    assignedByUserId = db.Column(db.Integer(), index=True)
    dateComplete = db.Column(db.DateTime(), index=True)
    notes = db.Column(db.Text(255), index=True)
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """The root level: Handles authentication and owns all chat sessions."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    
    # One User -> Many Chat Sessions
    sessions = db.relationship('ChatSession', backref='owner', lazy=True)

class ChatSession(db.Model):
    """The middle level: Groups messages together so they can be searched or resumed."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default="New Conversation")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Key linking back to the User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # One Session -> Many Messages
    # cascade="all, delete-orphan" ensures if a session is deleted, its messages are wiped too.
    messages = db.relationship('Message', backref='session', lazy=True, cascade="all, delete-orphan")

class Message(db.Model):
    """The ground level: Stores the actual back-and-forth text."""
    id = db.Column(db.Integer, primary_key=True)
    # Role will either be 'USER' or 'CHATBOT'
    role = db.Column(db.String(50), nullable=False) 
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Key linking back to the specific Chat Session
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
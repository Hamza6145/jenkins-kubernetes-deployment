from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # New attribute
    tv_shows = db.relationship('UserTVShow', backref='user', lazy=True)


class TVShow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season_name = db.Column(db.String(100), nullable=False)  # New attribute
    total_episodes = db.Column(db.Integer, nullable=False)  # New attribute
    cast_main_roles = db.Column(db.String(500), nullable=False)  # New attribute
    genre = db.Column(db.String(50), nullable=False)
    year_released = db.Column(db.Integer, nullable=False)  # New attribute
    platform = db.Column(db.String(100), nullable=False)  # New attribute
    users = db.relationship('UserTVShow', backref='tv_show', lazy=True)

class UserTVShow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tv_show_id = db.Column(db.Integer, db.ForeignKey('tv_show.id'), nullable=False)


class UserSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    search_query = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='searches')

class UserRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recommended_shows = db.Column(db.String(255), nullable=False)  # Comma separated show names or IDs
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='recommendations')

User.searches = db.relationship('UserSearch', back_populates='user')
User.recommendations = db.relationship('UserRecommendation', back_populates='user')

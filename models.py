"""
Database Models for John & Eniola Consultancy
"""

from datetime import datetime
import secrets
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.mysql import LONGTEXT

from extensions import db


class User(UserMixin, db.Model):
    """Admin User Model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=False)
    activation_token = db.Column(db.String(100), unique=True, index=True)
    reset_token = db.Column(db.String(100), unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def generate_activation_token(self):
        self.activation_token = secrets.token_urlsafe(32)
        return self.activation_token

    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        return self.reset_tokens


class SiteSettings(db.Model):
    """Global Site Settings"""
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False, default='John & Eniola Consultancy')
    company_description = db.Column(db.Text)
    phone_primary = db.Column(db.String(20))
    phone_secondary = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    social_links = db.Column(db.JSON, default=lambda: {})  # {"twitter": "...", "facebook": "...", etc}
    logo_image_path = db.Column(db.String(255), default='/static/images/logo.png')
    logo_dark_image_path = db.Column(db.String(255), default='/static/images/logo-dark.png')
    hero_background_image = db.Column(db.String(255), default='/static/images/hero-bg.jpg')
    favicon_path = db.Column(db.String(255), default='/static/images/favicon.ico')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Service(db.Model):
    """Service Offerings"""
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    slug = db.Column(db.String(255), unique=True)
    description = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(500))
    icon = db.Column(db.String(100))  # Icon class or emoji
    key_features = db.Column(db.JSON, default=list)  # List of feature strings
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BlogPost(db.Model):
    """Blog Posts / Insights"""
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    excerpt = db.Column(db.String(500))
    content = db.Column(LONGTEXT, nullable=False)
    featured_image = db.Column(db.String(255))
    author_name = db.Column(db.String(120), default='John & Eniola Team')
    category = db.Column(db.String(100), default='Insights')
    tags = db.Column(db.JSON, default=list)
    is_published = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Relationships
    comments = db.relationship('Comment', backref='blog_post', lazy=True, cascade='all, delete-orphan')


class Comment(db.Model):
    """Comments on Blog Posts (with nested reply support)"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  # For nested replies
    author_name = db.Column(db.String(120), nullable=False)
    author_email = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    edit_token = db.Column(db.String(255), unique=True, nullable=False, index=True, default=lambda: secrets.token_urlsafe(32) )
    is_approved = db.Column(db.Boolean, default=False)  # Admin moderation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Self-referential relationship for replies
    replies = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy=True
    )

   
class TestimonialSubmission(db.Model):
    """Temporary link for clients to submit testimonials"""
    __tablename__ = 'testimonial_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    client_name = db.Column(db.String(255), nullable=False)
    client_company = db.Column(db.String(255))           # Filled by Admin
    email = db.Column(db.String(120), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Link to final testimonial after submission
    testimonial_id = db.Column(db.Integer, db.ForeignKey('testimonials.id'), nullable=True)


class Testimonial(db.Model):
    """Approved Testimonials shown on website"""
    __tablename__ = 'testimonials'
    
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(255), nullable=False)
    client_role = db.Column(db.String(255))              # Filled by Client
    client_company = db.Column(db.String(255))           # Filled by Admin
    client_image = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=False)     # Must be approved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Link back to submission
    submission = db.relationship('TestimonialSubmission', backref='testimonial', uselist=False)

class TeamMember(db.Model):
    """Team Members"""
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text)
    email = db.Column(db.String(120))
    image = db.Column(db.String(255))
    social_links = db.Column(db.JSON, default=dict)
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Subscriber(db.Model):
    """Newsletter Subscribers"""
    __tablename__ = 'subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Newsletter(db.Model):
    """Newsletter Content / Template (PDF + Details)"""
    __tablename__ = 'newsletters'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    excerpt = db.Column(db.String(500))
    # content = db.Column(db.Text, nullable=False)          # Email body / description
    google_drive_link = db.Column(db.String(500))
    # pdf_url = db.Column(db.String(500))
    featured_image = db.Column(db.String(255))
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to campaigns
    campaigns = db.relationship('NewsletterCampaign', backref='newsletter', lazy=True)

    def has_been_sent(self):
        return NewsletterCampaign.query.filter_by(
            newsletter_id=self.id,
            is_sent=True
        ).first() is not None


class NewsletterCampaign(db.Model):
    """Tracks each time a newsletter is sent"""
    __tablename__ = 'newsletter_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    newsletter_id = db.Column(db.Integer, db.ForeignKey('newsletters.id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    sent_count = db.Column(db.Integer, default=0)
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def post_type(self):
        return "Newsletter"

class Media(db.Model):
    """Media Files (images, etc.)"""
    __tablename__ = 'media'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False, unique=True)
    mime_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer)  # in bytes
    alt_text = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HeroSlide(db.Model):
    """Hero Carousel Slides with Local Image Upload"""
    __tablename__ = 'hero_slides'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.Text)
    image_path = db.Column(db.String(500), nullable=False)   # Local file path
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<HeroSlide {self.title}>"

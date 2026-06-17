"""
Flask-WTF Forms for John & Eniola Consultancy
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SubmitField, SelectField, IntegerField, URLField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from models import User


class LoginForm(FlaskForm):
    """Admin Login Form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ContactForm(FlaskForm):
    """Contact Page Form"""
    name = StringField('Your name', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Your email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=3, max=255)])
    message = TextAreaField('Your message', validators=[Optional(), Length(max=5000)])
    submit = SubmitField('Submit')

class NewsletterForm(FlaskForm):
    """Create / Edit Newsletter Content"""
    title = StringField('Newsletter Title', validators=[DataRequired(), Length(max=255)])
    slug = StringField('Slug', validators=[DataRequired(), Length(max=255)])
    excerpt = TextAreaField('Excerpt')
    content = TextAreaField('Email Body / Description', validators=[DataRequired()])
    google_drive_link = URLField('Google Drive Link', validators=[DataRequired()])
    pdf_url = URLField('Direct PDF URL (Optional)')
    featured_image = FileField('Featured Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    is_published = BooleanField('Publish on Website', default=True)
    submit = SubmitField('Save Newsletter')


class NewsletterCampaignForm(FlaskForm):
    """Form for Sending Newsletter"""
    newsletter_id = SelectField('Select Newsletter', coerce=int, validators=[DataRequired()])
    subject = StringField('Custom Email Subject', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Send to All Subscribers')

    
class SubscribeNewsletterForm(FlaskForm):
    """Newsletter Subscription Form"""
    email = StringField('Your email', validators=[DataRequired(), Email()])
    name = StringField('Your name (optional)', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Subscribe')


class CommentForm(FlaskForm):
    """Blog Comment Form"""
    author_name = StringField('Name', validators=[DataRequired(), Length(min=2, max=120)])
    author_email = StringField('Email', validators=[DataRequired(), Email()])
    content = TextAreaField('Comment', validators=[DataRequired(), Length(min=5, max=5000)])
    submit = SubmitField('Post Comment')


class BlogPostForm(FlaskForm):
    """Create/Edit Blog Post"""
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=255)])
    slug = StringField('Slug', validators=[DataRequired(), Length(min=3, max=255)])
    excerpt = StringField('Excerpt', validators=[Optional(), Length(max=500)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=10)])
    featured_image = FileField('Featured Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    author_name = StringField('Author Name', validators=[Optional(), Length(max=120)])
    category = StringField('Category', validators=[Optional(), Length(max=100)])
    tags = StringField('Tags (comma-separated)', validators=[Optional()])
    is_published = BooleanField('Publish')
    submit = SubmitField('Save Post')


class ServiceForm(FlaskForm):
    """Create/Edit Service"""
    title = StringField('Service Title', validators=[DataRequired(), Length(min=3, max=255)])
    slug = StringField('Slug', validators=[DataRequired(), Length(min=3, max=255)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    excerpt = StringField('Excerpt', validators=[Optional(), Length(max=500)])
    icon = StringField('Icon (class or emoji)', validators=[Optional(), Length(max=100)])
    key_features = TextAreaField('Key Features (one per line)', validators=[Optional()])
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)])
    is_active = BooleanField('Active')
    submit = SubmitField('Save Service')


class TeamMemberForm(FlaskForm):
    """Create/Edit Team Member"""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=255)])
    role = StringField('Role/Title', validators=[DataRequired(), Length(min=2, max=255)])
    bio = TextAreaField('Biography', validators=[Optional(), Length(max=5000)])
    email = StringField('Email', validators=[Optional(), Email()])
    image = FileField('Profile Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)])
    is_active = BooleanField('Active')
    submit = SubmitField('Save Team Member')


class TestimonialForm(FlaskForm):
    """Create/Edit Testimonial"""
    client_name = StringField('Client Name', validators=[DataRequired(), Length(min=2, max=255)])
    client_role = StringField('Client Role/Company', validators=[Optional(), Length(max=255)])
    content = TextAreaField('Testimonial', validators=[DataRequired(), Length(min=10, max=5000)])
    client_image = FileField('Client Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    rating = IntegerField('Rating (1-5)', validators=[NumberRange(min=1, max=5)])
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)])
    is_active = BooleanField('Active')
    submit = SubmitField('Save Testimonial')


class SiteSettingsForm(FlaskForm):
    """Edit Global Site Settings"""
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=255)])
    company_description = TextAreaField('Company Description', validators=[Optional()])
    phone_primary = StringField('Primary Phone', validators=[Optional(), Length(max=20)])
    phone_secondary = StringField('Secondary Phone', validators=[Optional(), Length(max=20)])
    email = StringField('Email Address', validators=[Optional(), Email()])
    address = TextAreaField('Physical Address', validators=[Optional()])
    
    # Logo uploads
    logo_image = FileField('Logo Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'svg'], 'Images only!')
    ])
    logo_dark_image = FileField('Dark Logo Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'svg'], 'Images only!')
    ])
    
    # Social links
    twitter = StringField('Twitter URL', validators=[Optional()])
    facebook = StringField('Facebook URL', validators=[Optional()])
    linkedin = StringField('LinkedIn URL', validators=[Optional()])
    instagram = StringField('Instagram URL', validators=[Optional()])
    
    submit = SubmitField('Save Settings')


class NewsletterCampaignForm(FlaskForm):
    """Create/Send Newsletter"""
    subject = StringField('Newsletter Subject', validators=[DataRequired(), Length(min=3, max=255)])
    content = TextAreaField('Newsletter Content', validators=[DataRequired(), Length(min=10)])
    google_drive_link = StringField('Google Drive Link (optional)', validators=[Optional()])
    submit = SubmitField('Send Newsletter')


class CreateUserForm(FlaskForm):
    """Create Admin User"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create User')
    
    def validate_username(self, username):
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

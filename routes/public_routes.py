"""
Public Routes for John & Eniola Consultancy Website
"""
import os
import secrets
from flask import Blueprint, flash, json, render_template, request, jsonify, current_app, url_for, json, jsonify
import requests
from flask_mail import Message
from sqlalchemy import desc
from werkzeug.utils import redirect
from models import (
    BlogPost, HeroSlide, Newsletter, Service, Testimonial, TeamMember, Subscriber, 
    Comment, SiteSettings, Media, TestimonialSubmission, User
)
from forms import ContactForm, ForgotPasswordForm, NewsletterForm, CommentForm, PublicTestimonialForm, ResetPasswordForm, SetPasswordForm, SubscribeNewsletterForm
from app import db, mail
from bleach import clean
from datetime import datetime
from dotenv import load_dotenv

from utils import send_password_reset_email

load_dotenv()  # Load environment variables from .env file

public_bp = Blueprint('public', __name__)


CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID')
API_KEY = os.getenv('YOUTUBE_API_KEY')
CACHE_FILE = 'youtube_cache.json'
CACHE_DURATION = 3600  # 1 hour in seconds


def get_youtube_videos():
    videos = []
    cache_loaded = False

    # Try to load cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                if datetime.now().timestamp() - cache.get('timestamp', 0) < CACHE_DURATION:
                    videos = cache.get('videos', [])
                    cache_loaded = True
                    print("Loaded from cache")
        except:
            pass

    if cache_loaded and videos:
        return videos

    # Fetch from YouTube
    try:
        print("Fetching from YouTube API...")

        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={CHANNEL_ID}&maxResults=10&order=date&type=video&key={API_KEY}"
        
        response = requests.get(url, timeout=15)
        
        print(f"API Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(f"Videos found: {len(items)}")

            for item in items:
                snippet = item['snippet']
                video_id = item.get('id', {}).get('videoId')
              
                if not video_id:
                    continue

                videos.append({
                    'id': video_id,
                    'title': snippet['title'],
                    'description': snippet.get('description', ''),
                    'thumb': snippet['thumbnails'].get('high', {}).get('url') or 
                             snippet['thumbnails'].get('medium', {}).get('url') or 
                             snippet['thumbnails'].get('default', {}).get('url'),
                    'published': datetime.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").strftime("%b %d, %Y")
                })

            # Save cache
            try:
                with open(CACHE_FILE, 'w') as f:
                    json.dump({
                        'timestamp': datetime.now().timestamp(),
                        'videos': videos
                    }, f)
                print("Cache saved")
            except:
                pass

        else:
            print("API Error Response:", response.text[:300])

    except Exception as e:
        print(f"Exception: {e}")

    return videos

def get_site_settings():
    """Get global site settings"""
    return SiteSettings.query.first() or SiteSettings()

@public_bp.context_processor
def inject_site_settings():
    """Make site settings available in all templates"""
    return {'site_settings': get_site_settings()}



@public_bp.route('/test-email')
def test_email():
    try:
        msg = Message(
            subject="Test Email",
            recipients=["officialudobad@gmail.com"],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        msg.body = "This is a test email from your Flask app."
        mail.send(msg)
        return "Test email sent successfully!"
    except Exception as e:
        return f"Error: {str(e)}"

@public_bp.route('/')
def home():
    
    """Home Page"""
    services = Service.query.filter_by(is_active=True).order_by(Service.order).limit(6).all()
    testimonials = Testimonial.query.filter_by(is_active=True).order_by(Testimonial.order).all()
    latest_posts = BlogPost.query.filter_by(is_published=True).order_by(desc(BlogPost.published_at)).limit(9).all()
    hero_slides = HeroSlide.query.filter_by(is_active=True).order_by(HeroSlide.order).all()
    videos = get_youtube_videos()
    print(f"Passing {len(videos)} videos to template")
    return render_template('public/home.html', 
                         services=services,
                         testimonials=testimonials,
                         latest_posts=latest_posts,
                         videos=videos,
                         hero_slides=hero_slides)


@public_bp.route('/about')
def about():
    """About Page"""
    team_members = TeamMember.query.filter_by(is_active=True).order_by(TeamMember.order).all()
    return render_template('public/about.html', team_members=team_members)


@public_bp.route('/services')
def services():
    """Services Page"""
    services = Service.query.filter_by(is_active=True).order_by(Service.order).all()
    return render_template('public/services.html', services=services)


@public_bp.route('/insights')
def insights():
    """Insights/Blog Page"""
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(is_published=True).order_by(
        desc(BlogPost.published_at)
    ).paginate(page=page, per_page=9)
    
    return render_template('public/insights.html', posts=posts)

@public_bp.route('/insights/<string:slug>', methods=['GET', 'POST'])
def blog_detail(slug):
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    post.view_count += 1
    db.session.commit()

    form = CommentForm()

    if form.validate_on_submit():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                parent_id = request.form.get('parent_id', type=int)
                
                comment = Comment(
                    blog_post_id=post.id,
                    author_name=clean(form.author_name.data),
                    author_email=form.author_email.data,
                    content=clean(form.content.data),
                    parent_id=parent_id,
                    is_approved=False  # All new comments/replies need approval
                )
                db.session.add(comment)
                db.session.commit()

                manage_url = url_for(                     
                    'public.manage_comment',                     
                    token=comment.edit_token,                     
                    _external=True                 
                    )                 
                msg = Message(                     
                    subject='Manage Your Comment',                     
                    recipients=[comment.author_email]                 
                    )                 
                
                msg.html = render_template(
                    'emails/comment_manager.html',
                    post=post,
                    comment=comment,
                    manage_url=manage_url,
                    current_year=datetime.now().year
                )

                mail.send(msg)

                return jsonify({
                    'success': True,
                    'message': 'Your comment has been submitted and is awaiting moderation.'
                }), 201
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 400

    # Get ONLY approved comments and their approved replies
    comments = Comment.query.filter_by(
        blog_post_id=post.id,
        is_approved=True,
        parent_id=None
    ).order_by(Comment.created_at.desc()).all()

    # Get related posts
    related_posts = BlogPost.query.filter(
        BlogPost.id != post.id,
        BlogPost.is_published == True
    ).order_by(desc(BlogPost.published_at)).limit(3).all()

    return render_template('public/blog-detail.html',
                         post=post,
                         form=form,
                         comments=comments,
                         related_posts=related_posts)

@public_bp.route('/newsletters')
def newsletters():
    """Dedicated Newsletter List Page"""
    page = request.args.get('page', 1, type=int)
    newsletters = Newsletter.query.filter_by(is_published=True)\
                    .order_by(desc(Newsletter.published_at))\
                    .paginate(page=page, per_page=9)
    
    return render_template('public/newsletters.html', newsletters=newsletters)


@public_bp.route('/newsletter/<string:slug>')
def newsletter_detail(slug):
    """Single Newsletter Detail with PDF Viewer"""
    newsletter = Newsletter.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    return render_template('public/newsletter_detail.html', newsletter=newsletter)

@public_bp.route('/comment/manage/<token>')
def manage_comment(token):

    comment = Comment.query.filter_by(
        edit_token=token
    ).first_or_404()

    return render_template(
        'comment/manage.html',
        comment=comment
    )

@public_bp.route(
    '/comment/manage/<token>/edit',
    methods=['POST']
)
def edit_comment(token):

    comment = Comment.query.filter_by(
        edit_token=token
    ).first_or_404()

    comment.content = request.form.get('content')

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Comment updated.'
    })

@public_bp.route(
    '/comment/manage/<token>/delete',
    methods=['POST']
)
def delete_comment(token):

    comment = Comment.query.filter_by(
        edit_token=token
    ).first_or_404()

    db.session.delete(comment)

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Comment deleted.'
    })



@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact Page"""
    form = ContactForm()
    
    if form.validate_on_submit():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request
            try:
                # Send email to admin
                msg = Message(
                    subject=f'New Contact Form: {form.subject.data}',
                    recipients=[get_site_settings().email or 'info@johneniola.com'],
                    body=f"""
                    New message from contact form:
                    
                    Name: {form.name.data}
                    Email: {form.email.data}
                    Subject: {form.subject.data}
                    
                    Message:
                    {form.message.data}
                    """
                )
                mail.send(msg)
                
                return jsonify({
                    'success': True,
                    'message': 'Thank you for your message. We will get back to you soon.'
                }), 200
            except Exception as e:
                current_app.logger.error(f'Error sending contact email: {str(e)}')
                return jsonify({
                    'success': False,
                    'message': 'Error sending message. Please try again.'
                }), 400
    
    return render_template('public/contact.html', form=form)


@public_bp.route('/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    """Newsletter Subscription (AJAX)"""
    form = SubscribeNewsletterForm()
    
    if form.validate_on_submit():
        try:
            # Check if already subscribed
            existing = Subscriber.query.filter_by(email=form.email.data).first()
            
            if existing:
                if not existing.is_active:
                    existing.is_active = True
                    db.session.commit()
                return jsonify({
                    'success': False,
                    'message': 'You are already subscribed!'
                }), 200
            
            # Add new subscriber
            subscriber = Subscriber(
                email=form.email.data,
                name=form.name.data or None
            )
            db.session.add(subscriber)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Thank you for subscribing!'
            }), 201
        except Exception as e:
            current_app.logger.error(f'Error subscribing to newsletter: {str(e)}')
            return jsonify({
                'success': False,
                'message': 'Error processing subscription.'
            }), 400
    
    return jsonify({
        'success': False,
        'message': 'Validation failed.',
        'errors': form.errors
    }), 400


@public_bp.route('/unsubscribe')
def unsubscribe():
    """Public Unsubscribe Page"""
    email = request.args.get('email', '').strip().lower()

    if email:
        subscriber = Subscriber.query.filter_by(email=email).first()

        if subscriber:
            try:
                db.session.delete(subscriber)
                db.session.commit()
                return render_template(
                    'public/unsubscribe.html',
                    success=True,
                    email=email
                )
            except Exception:
                db.session.rollback()

    return render_template('public/unsubscribe.html', success=False)


@public_bp.route('/api/comments/<int:post_id>')
def get_comments(post_id):
    """Get approved comments for a post (API endpoint)"""
    comments = Comment.query.filter_by(
        blog_post_id=post_id,
        is_approved=True,
        parent_id=None
    ).order_by(desc(Comment.created_at)).all()
    
    def serialize_comment(comment):
        return {
            'id': comment.id,
            'author_name': comment.author_name,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            'replies': [serialize_comment(reply) for reply in comment.replies]
        }
    
    return jsonify([serialize_comment(c) for c in comments])


# ============================ ========================== 
@public_bp.route('/activate/<token>', methods=['GET', 'POST'])
def activate_account(token):
    user = User.query.filter_by(activation_token=token).first_or_404()
    
    if user.is_active:
        flash('Account already activated.', 'info')
        return redirect(url_for('admin.login'))
    
    form = SetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.is_active = True
        user.activation_token = None
        db.session.commit()
        
        flash('Account activated successfully! You can now login.', 'success')
        return redirect(url_for('admin.login'))
    
    return render_template('admin/activate.html', form=form, user=user)


@public_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            db.session.commit()
            send_password_reset_email(user, token)
        
        flash('If an account exists with that email, a reset link has been sent.', 'info')
        return redirect(url_for('admin.login'))
    
    return render_template('admin/forgot_password.html', form=form)


@public_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first_or_404()
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None
        db.session.commit()
        
        flash('Password reset successful. Please login.', 'success')
        return redirect(url_for('admin.login'))
    
    return render_template('admin/reset_password.html', form=form)


@public_bp.route('/submit-testimonial/<token>', methods=['GET', 'POST'])
def submit_testimonial(token):
    submission = TestimonialSubmission.query.filter_by(token=token).first_or_404()

    if submission.is_used or submission.expires_at < datetime.utcnow():
        return render_template('public/testimonial_expired.html')

    form = PublicTestimonialForm()

    if form.validate_on_submit():
        testimonial = Testimonial(
            client_name=submission.client_name,
            client_role=form.client_role.data,
            client_company=submission.client_company,
            content=form.content.data,
            rating=form.rating.data,
            is_active=False  # Requires admin approval
        )
        db.session.add(testimonial)
        db.session.commit()

        submission.testimonial_id = testimonial.id
        submission.is_used = True
        db.session.commit()

        flash('Thank you! Your testimonial has been received and is under review.', 'success')
        return redirect(url_for('public.home'))

    return render_template('public/submit_testimonial.html', form=form, submission=submission)

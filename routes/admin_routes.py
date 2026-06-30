"""
Admin Routes for John & Eniola Consultancy Dashboard
"""

import secrets
from urllib.parse import urljoin, urlparse

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, flash
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from functools import wraps
import os
from datetime import datetime, timedelta

from models import (
    HeroSlide, NewsletterCampaign, TestimonialSubmission, User, BlogPost, Service, TeamMember, Testimonial, 
    Subscriber, Newsletter, Comment, SiteSettings, Media
)
from forms import (
    AdminRegisterForm, HeroSlideForm, LoginForm, BlogPostForm, NewsletterForm, ServiceForm, TeamMemberForm, 
    TestimonialForm, SiteSettingsForm, NewsletterCampaignForm, TestimonialLinkForm
)
from app import db, mail
from flask_mail import Message

from tasks import send_email_task
from utils import send_activation_email, send_newsletter_email, send_testimonial_invite_email

admin_bp = Blueprint('admin', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload_file(file, subfolder=None):
    """
    Save uploaded file and return a URL path.

    Examples:
        save_upload_file(file)
        -> /static/uploads/image.jpg

        save_upload_file(file, "hero")
        -> /static/uploads/hero/image.jpg

        save_upload_file(file, "products/electronics")
        -> /static/uploads/products/electronics/image.jpg
    """
    if not file or not file.filename or not allowed_file(file.filename):
        return None

    filename = secure_filename(
        f"{datetime.now().timestamp()}_{file.filename}"
    )

    # Build upload directory
    upload_dir = UPLOAD_FOLDER
    if subfolder:
        upload_dir = os.path.join(UPLOAD_FOLDER, subfolder)

    # Create directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Return browser-friendly URL
    return "/" + filepath.replace(os.sep, "/")


def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/media/upload', methods=['POST'])
@admin_required
def upload_media():

    file = request.files.get('file')

    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    filepath = save_upload_file(file)

    media = Media(
        filename=file.filename,
        filepath=filepath,
        mime_type=file.mimetype,
        file_size=0
    )

    db.session.add(media)
    db.session.commit()

    return jsonify({
        "location": filepath
    })




@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin Login"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('admin.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        
        if not next_page or url_has_allowed_host_and_scheme(next_page):
            next_page = url_for('admin.dashboard')
        
        return redirect(next_page)
    
    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    """Admin Logout"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('public.home'))


@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin Dashboard"""
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)

    total_posts = BlogPost.query.count()
    published_posts = BlogPost.query.filter_by(is_published=True).count()
    draft_posts = total_posts - published_posts

    total_newsletters = Newsletter.query.count()
    published_newsletters = Newsletter.query.filter_by(is_published=True).count()
    sent_campaigns = NewsletterCampaign.query.filter_by(is_sent=True).count()

    all_subscribers = Subscriber.query.count()
    active_subscribers = Subscriber.query.filter_by(is_active=True).count()
    recent_subscribers = Subscriber.query.filter(
        Subscriber.created_at >= thirty_days_ago
    ).count()

    total_comments = Comment.query.count()
    approved_comments = Comment.query.filter_by(is_approved=True).count()
    pending_comments = total_comments - approved_comments

    stats = {
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_services': Service.query.count(),
        'total_team': TeamMember.query.count(),
        'total_subscribers': all_subscribers,
        'active_subscribers': active_subscribers,
        'recent_subscribers': recent_subscribers,
        'total_comments': total_comments,
        'approved_comments': approved_comments,
        'pending_comments': pending_comments,
        'total_testimonials': Testimonial.query.count(),
        'active_testimonials': Testimonial.query.filter_by(is_active=True).count(),
        'total_hero_slides': HeroSlide.query.count(),
        'active_hero_slides': HeroSlide.query.filter_by(is_active=True).count(),
        'total_newsletters': total_newsletters,
        'published_newsletters': published_newsletters,
        'total_admins': User.query.filter_by(is_admin=True).count(),
        'sent_campaigns': sent_campaigns,
        'post_view_count': db.session.query(db.func.sum(BlogPost.view_count)).scalar() or 0,
    }

    recent_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(5).all()
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
    recent_subscribers_list = Subscriber.query.order_by(Subscriber.created_at.desc()).limit(5).all()
    recent_campaigns = NewsletterCampaign.query.order_by(NewsletterCampaign.sent_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_posts=recent_posts,
        recent_comments=recent_comments,
        recent_subscribers=recent_subscribers_list,
        recent_campaigns=recent_campaigns
    )


@admin_bp.route('/analytics')
@admin_required
def analytics():
    """Analytics Dashboard"""
    from sqlalchemy import func, cast, Date

    # Aggregate stats
    total_posts = BlogPost.query.count()
    total_services = Service.query.count()
    total_subscribers = Subscriber.query.count()
    total_comments = Comment.query.count()
    total_newsletters = Newsletter.query.count()
    total_testimonials = Testimonial.query.count()
    total_team = TeamMember.query.count()
    post_view_count = db.session.query(func.sum(BlogPost.view_count)).scalar() or 0

    # Most viewed posts (top 10)
    top_posts = BlogPost.query.order_by(BlogPost.view_count.desc()).limit(10).all()

    # Posts by category
    category_counts = db.session.query(
        BlogPost.category, func.count(BlogPost.id)
    ).filter(
        BlogPost.category.isnot(None), BlogPost.category != ''
    ).group_by(BlogPost.category).order_by(func.count(BlogPost.id).desc()).all()

    # Subscriber growth (last 30 days, grouped by date)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    subscriber_daily = db.session.query(
        cast(Subscriber.created_at, Date), func.count(Subscriber.id)
    ).filter(
        Subscriber.created_at >= thirty_days_ago
    ).group_by(cast(Subscriber.created_at, Date)).order_by(cast(Subscriber.created_at, Date)).all()

    # Comments trend (last 30 days)
    comment_daily = db.session.query(
        cast(Comment.created_at, Date), func.count(Comment.id)
    ).filter(
        Comment.created_at >= thirty_days_ago
    ).group_by(cast(Comment.created_at, Date)).order_by(cast(Comment.created_at, Date)).all()

    # Posts published trend (last 12 months)
    twelve_months_ago = datetime.utcnow() - timedelta(days=365)
    post_monthly = db.session.query(
        func.date_format(BlogPost.created_at, '%%Y-%%m').label('month'),
        func.count(BlogPost.id)
    ).filter(
        BlogPost.created_at >= twelve_months_ago
    ).group_by('month').order_by('month').all()

    # Published vs Draft ratio
    published_count = BlogPost.query.filter_by(is_published=True).count()
    draft_count = total_posts - published_count

    # Active vs Inactive services
    active_services = Service.query.filter_by(is_active=True).count()
    inactive_services = total_services - active_services

    # Subscriber active/inactive
    active_subs = Subscriber.query.filter_by(is_active=True).count()
    inactive_subs = total_subscribers - active_subs

    # Comment approval ratio
    approved_comments = Comment.query.filter_by(is_approved=True).count()
    pending_comments = total_comments - approved_comments

    # Newsletter sent count
    sent_newsletters = NewsletterCampaign.query.filter_by(is_sent=True).count()

    return render_template(
        'admin/analytics.html',
        top_posts=top_posts,
        category_counts=category_counts,
        subscriber_daily=subscriber_daily,
        comment_daily=comment_daily,
        post_monthly=post_monthly,
        total_posts=total_posts,
        total_services=total_services,
        total_subscribers=total_subscribers,
        total_comments=total_comments,
        total_newsletters=total_newsletters,
        total_testimonials=total_testimonials,
        total_team=total_team,
        post_view_count=post_view_count,
        published_count=published_count,
        draft_count=draft_count,
        active_services=active_services,
        inactive_services=inactive_services,
        active_subs=active_subs,
        inactive_subs=inactive_subs,
        approved_comments=approved_comments,
        pending_comments=pending_comments,
        sent_newsletters=sent_newsletters,
    )


# ============ BLOG POST MANAGEMENT ============

@admin_bp.route('/blog')
@admin_required
def blog_list():
    """List all blog posts"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    category_filter = request.args.get('category', '').strip()

    query = BlogPost.query

    if search:
        query = query.filter(
            db.or_(
                BlogPost.title.ilike(f'%{search}%'),
                BlogPost.author_name.ilike(f'%{search}%'),
                BlogPost.category.ilike(f'%{search}%')
            )
        )
    if status_filter == 'published':
        query = query.filter(BlogPost.is_published == True)
    elif status_filter == 'draft':
        query = query.filter(BlogPost.is_published == False)
    if category_filter:
        query = query.filter(BlogPost.category.ilike(f'%{category_filter}%'))

    posts = query.order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=20)

    categories = [row[0] for row in db.session.query(BlogPost.category).distinct().all() if row[0]]

    return render_template('admin/blog/list.html', posts=posts, search=search, status_filter=status_filter, category_filter=category_filter, categories=categories)


@admin_bp.route('/blog/create', methods=['GET', 'POST'])
@admin_required
def blog_create():
    """Create new blog post"""
    form = BlogPostForm()
    
    if form.validate_on_submit():
        featured_image_path = None
        if form.featured_image.data:
            featured_image_path = save_upload_file(form.featured_image.data, "blog")
        
        tags = [tag.strip() for tag in form.tags.data.split(',')] if form.tags.data else []
        
        author_name = form.author_name.data or current_user.full_name or 'John & Eniola Team'

        # Calculate reading time (~200 words per minute)
        word_count = len(form.content.data.split())
        reading_time = max(1, round(word_count / 200))
        
        post = BlogPost(
            title=form.title.data,
            slug=form.slug.data,
            excerpt=form.excerpt.data,
            content=form.content.data,
            featured_image=featured_image_path,
            author_name=author_name,
            category=form.category.data or 'Insights',
            tags=tags,
            meta_description=form.meta_description.data,
            is_featured=form.is_featured.data,
            reading_time=reading_time,
            is_published=form.is_published.data,
            published_at=datetime.utcnow() if form.is_published.data else None
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('admin.blog_list'))
    
    if not form.author_name.data:
        form.author_name.data = current_user.full_name
    return render_template('admin/blog/form.html', form=form, action='Create')


@admin_bp.route('/blog/<int:post_id>/edit', methods=['GET', 'POST'])
@admin_required
def blog_edit(post_id):
    """Edit blog post"""
    post = BlogPost.query.get_or_404(post_id)
    form = BlogPostForm()
    
    if form.validate_on_submit():
        if form.featured_image.data:
            featured_image_path = save_upload_file(form.featured_image.data, "blog")
            post.featured_image = featured_image_path
        
        post.title = form.title.data
        post.slug = form.slug.data
        post.excerpt = form.excerpt.data
        post.content = form.content.data
        post.author_name = form.author_name.data or 'John & Eniola Team'
        post.category = form.category.data or 'Insights'
        post.is_published = form.is_published.data
        post.meta_description = form.meta_description.data
        post.is_featured = form.is_featured.data
        
        # Recalculate reading time
        word_count = len(form.content.data.split())
        post.reading_time = max(1, round(word_count / 200))
        
        if form.tags.data:
            post.tags = [tag.strip() for tag in form.tags.data.split(',')]
        
        if form.is_published.data and not post.published_at:
            post.published_at = datetime.utcnow()
        
        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin.blog_list'))
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.slug.data = post.slug
        form.excerpt.data = post.excerpt
        form.content.data = post.content
        form.author_name.data = post.author_name
        form.category.data = post.category
        form.tags.data = ', '.join(post.tags) if post.tags else ''
        form.meta_description.data = post.meta_description
        form.is_featured.data = post.is_featured
        form.is_published.data = post.is_published
    
    return render_template('admin/blog/form.html', form=form, action='Edit', post=post)


@admin_bp.route('/blog/<int:post_id>/delete', methods=['POST'])
@admin_required
def blog_delete(post_id):
    """Delete blog post"""
    post = BlogPost.query.get_or_404(post_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            db.session.delete(post)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Blog post deleted.'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('admin.blog_list'))


@admin_bp.route('/blog/bulk-action', methods=['POST'])
@admin_required
def blog_bulk_action():
    """Bulk actions on blog posts (publish, unpublish, delete)"""
    action = request.form.get('action')
    post_ids = request.form.getlist('post_ids[]')

    if not action or not post_ids:
        flash('No posts selected or no action specified.', 'warning')
        return redirect(url_for('admin.blog_list'))

    posts = BlogPost.query.filter(BlogPost.id.in_(post_ids)).all()

    if action == 'publish':
        now = datetime.utcnow()
        for post in posts:
            post.is_published = True
            if not post.published_at:
                post.published_at = now
        flash(f'{len(posts)} post(s) published.', 'success')
    elif action == 'unpublish':
        for post in posts:
            post.is_published = False
        flash(f'{len(posts)} post(s) unpublished.', 'success')
    elif action == 'delete':
        for post in posts:
            db.session.delete(post)
        flash(f'{len(posts)} post(s) deleted.', 'success')
    else:
        flash('Unknown action.', 'danger')

    db.session.commit()
    return redirect(url_for('admin.blog_list'))

# ============ SERVICE MANAGEMENT ============

@admin_bp.route('/services')
@admin_required
def services_list():
    """List all services"""
    services = Service.query.order_by(Service.order).all()
    return render_template('admin/services/list.html', services=services)


@admin_bp.route('/services/create', methods=['GET', 'POST'])
@admin_required
def service_create():
    """Create new service"""
    form = ServiceForm()
    
    if form.validate_on_submit():
        key_features = [f.strip() for f in form.key_features.data.split('\n') if f.strip()] if form.key_features.data else []
        
        service = Service(
            title=form.title.data,
            slug=form.slug.data,
            description=form.description.data,
            excerpt=form.excerpt.data,
            icon=form.icon.data,
            key_features=key_features,
            order=form.order.data or 0,
            is_active=form.is_active.data
        )
        
        db.session.add(service)
        db.session.commit()
        
        flash('Service created successfully!', 'success')
        return redirect(url_for('admin.services_list'))
    
    return render_template('admin/services/form.html', form=form, action='Create')


@admin_bp.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@admin_required
def service_edit(service_id):
    """Edit service"""
    service = Service.query.get_or_404(service_id)
    form = ServiceForm()
    
    if form.validate_on_submit():
        service.title = form.title.data
        service.slug = form.slug.data
        service.description = form.description.data
        service.excerpt = form.excerpt.data
        service.icon = form.icon.data
        service.order = form.order.data or 0
        service.is_active = form.is_active.data
        
        if form.key_features.data:
            service.key_features = [f.strip() for f in form.key_features.data.split('\n') if f.strip()]
        
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('admin.services_list'))
    
    elif request.method == 'GET':
        form.title.data = service.title
        form.slug.data = service.slug
        form.description.data = service.description
        form.excerpt.data = service.excerpt
        form.icon.data = service.icon
        form.order.data = service.order
        form.is_active.data = service.is_active
        form.key_features.data = '\n'.join(service.key_features) if service.key_features else ''
    
    return render_template('admin/services/form.html', form=form, action='Edit', service=service)


@admin_bp.route('/services/<int:service_id>/delete', methods=['POST'])
@admin_required
def service_delete(service_id):
    """Delete service"""
    service = Service.query.get_or_404(service_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            db.session.delete(service)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Service deleted.'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully!', 'success')
    return redirect(url_for('admin.services_list'))


# ============ TEAM MANAGEMENT ============

@admin_bp.route('/team')
@admin_required
def team_list():
    """List all team members"""
    team = TeamMember.query.order_by(TeamMember.order).all()
    return render_template('admin/team/list.html', team=team)


@admin_bp.route('/team/create', methods=['GET', 'POST'])
@admin_required
def team_create():
    """Create new team member"""
    form = TeamMemberForm()
    
    if form.validate_on_submit():
        image_path = None
        if form.image.data:
            image_path = save_upload_file(form.image.data, "team")
        
        member = TeamMember(
            name=form.name.data,
            role=form.role.data,
            bio=form.bio.data,
            email=form.email.data,
            image=image_path,
            order=form.order.data or 0,
            is_active=form.is_active.data
        )
        
        db.session.add(member)
        db.session.commit()
        
        flash('Team member created successfully!', 'success')
        return redirect(url_for('admin.team_list'))
    
    return render_template('admin/team/form.html', form=form, action='Create')


@admin_bp.route('/team/<int:member_id>/edit', methods=['GET', 'POST'])
@admin_required
def team_edit(member_id):
    """Edit team member"""
    member = TeamMember.query.get_or_404(member_id)
    form = TeamMemberForm()
    
    if form.validate_on_submit():
        if form.image.data:
            image_path = save_upload_file(form.image.data, "team")
            member.image = image_path
        
        member.name = form.name.data
        member.role = form.role.data
        member.bio = form.bio.data
        member.email = form.email.data
        member.order = form.order.data or 0
        member.is_active = form.is_active.data
        
        db.session.commit()
        flash('Team member updated successfully!', 'success')
        return redirect(url_for('admin.team_list'))
    
    elif request.method == 'GET':
        form.name.data = member.name
        form.role.data = member.role
        form.bio.data = member.bio
        form.email.data = member.email
        form.order.data = member.order
        form.is_active.data = member.is_active
    
    return render_template('admin/team/form.html', form=form, action='Edit', member=member)


@admin_bp.route('/team/<int:member_id>/delete', methods=['POST'])
@admin_required
def team_delete(member_id):
    """Delete team member"""
    member = TeamMember.query.get_or_404(member_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            db.session.delete(member)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Team member deleted.'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    
    db.session.delete(member)
    db.session.commit()
    flash('Team member deleted successfully!', 'success')
    return redirect(url_for('admin.team_list'))


# ============ TESTIMONIAL MANAGEMENT ============

@admin_bp.route('/testimonials')
@admin_required
def testimonials_list():
    """List all testimonials"""
    testimonials = Testimonial.query.order_by(Testimonial.order).all()
    return render_template('admin/testimonials/list.html', testimonials=testimonials)


@admin_bp.route('/testimonials/create', methods=['GET', 'POST'])
@admin_required
def testimonial_create():
    """Create new testimonial"""
    form = TestimonialForm()
    
    if form.validate_on_submit():
        image_path = None
        if form.client_image.data:
            image_path = save_upload_file(form.client_image.data, "testimonials")
        
        testimonial = Testimonial(
            client_name=form.client_name.data,
            client_role=form.client_role.data,
            content=form.content.data,
            client_image=image_path,
            rating=form.rating.data or 5,
            order=form.order.data or 0,
            is_active=form.is_active.data
        )
        
        db.session.add(testimonial)
        db.session.commit()
        
        flash('Testimonial created successfully!', 'success')
        return redirect(url_for('admin.testimonials_list'))
    
    return render_template('admin/testimonials/form.html', form=form, action='Create')


@admin_bp.route('/testimonials/<int:testimonial_id>/edit', methods=['GET', 'POST'])
@admin_required
def testimonial_edit(testimonial_id):
    """Edit testimonial"""
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    form = TestimonialForm()
    
    if form.validate_on_submit():
        if form.client_image.data:
            image_path = save_upload_file(form.client_image.data, "testimonials")
            testimonial.client_image = image_path
        
        testimonial.client_name = form.client_name.data
        testimonial.client_role = form.client_role.data
        testimonial.content = form.content.data
        testimonial.rating = form.rating.data or 5
        testimonial.order = form.order.data or 0
        testimonial.is_active = form.is_active.data
        
        db.session.commit()
        flash('Testimonial updated successfully!', 'success')
        return redirect(url_for('admin.testimonials_list'))
    
    elif request.method == 'GET':
        form.client_name.data = testimonial.client_name
        form.client_role.data = testimonial.client_role
        form.content.data = testimonial.content
        form.rating.data = testimonial.rating
        form.order.data = testimonial.order
        form.is_active.data = testimonial.is_active
    
    return render_template('admin/testimonials/form.html', form=form, action='Edit', testimonial=testimonial)





# ============ COMMENTS MANAGEMENT ============

@admin_bp.route('/comments')
@admin_required
def comments_list():
    """List all comments"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'pending')  # pending, approved
    
    if status == 'approved':
        comments = Comment.query.filter_by(is_approved=True).order_by(Comment.created_at.desc()).paginate(page=page, per_page=20)
    else:
        comments = Comment.query.filter_by(is_approved=False).order_by(Comment.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/comments/list.html', comments=comments, status=status)


@admin_bp.route('/comments/<int:comment_id>/approve', methods=['POST'])
@admin_required
def comment_approve(comment_id):
    """Approve a comment"""
    comment = Comment.query.get_or_404(comment_id)
    comment.is_approved = True
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Comment approved.'}), 200
    
    flash('Comment approved.', 'success')
    return redirect(url_for('admin.comments_list', status='pending'))


@admin_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@admin_required
def comment_delete(comment_id):
    """Delete a comment"""
    comment = Comment.query.get_or_404(comment_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            db.session.delete(comment)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Comment deleted.'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect(request.referrer or url_for('admin.comments_list'))


# ============ SITE SETTINGS ============

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def site_settings():
    """Edit global site settings"""
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()
    
    form = SiteSettingsForm()
    
    if form.validate_on_submit():
        settings.company_name = form.company_name.data
        settings.company_description = form.company_description.data
        settings.phone_primary = form.phone_primary.data
        settings.phone_secondary = form.phone_secondary.data
        settings.email = form.email.data
        settings.address = form.address.data
        
        # Handle logo uploads
        if form.logo_image.data:
            logo_path = save_upload_file(form.logo_image.data, "site")
            if logo_path:
                settings.logo_image_path = logo_path
        
        if form.logo_dark_image.data:
            logo_dark_path = save_upload_file(form.logo_dark_image.data, "site")
            if logo_dark_path:
                settings.logo_dark_image_path = logo_dark_path
        
        # Hero section
        settings.hero_title = form.hero_title.data
        settings.hero_subtitle = form.hero_subtitle.data
        settings.hero_btn_text = form.hero_btn_text.data
        settings.hero_btn_url = form.hero_btn_url.data

        # SEO fields
        settings.meta_title = form.meta_title.data
        settings.meta_description = form.meta_description.data
        settings.og_image = form.og_image.data
        settings.google_analytics_id = form.google_analytics_id.data
        settings.google_tag_manager_id = form.google_tag_manager_id.data

        # Handle social links
        social_links = {}
        if form.twitter.data:
            social_links['twitter'] = form.twitter.data
        if form.facebook.data:
            social_links['facebook'] = form.facebook.data
        if form.linkedin.data:
            social_links['linkedin'] = form.linkedin.data
        if form.instagram.data:
            social_links['instagram'] = form.instagram.data
        settings.social_links = social_links
        
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Settings updated successfully.'}), 200
        
        flash('Site settings updated successfully!', 'success')
        return redirect(url_for('admin.site_settings'))
    
    elif request.method == 'GET':
        form.company_name.data = settings.company_name
        form.company_description.data = settings.company_description
        form.phone_primary.data = settings.phone_primary
        form.phone_secondary.data = settings.phone_secondary
        form.email.data = settings.email
        form.address.data = settings.address

        form.hero_title.data = settings.hero_title
        form.hero_subtitle.data = settings.hero_subtitle
        form.hero_btn_text.data = settings.hero_btn_text
        form.hero_btn_url.data = settings.hero_btn_url

        # Load SEO fields
        form.meta_title.data = settings.meta_title
        form.meta_description.data = settings.meta_description
        form.og_image.data = settings.og_image
        form.google_analytics_id.data = settings.google_analytics_id
        form.google_tag_manager_id.data = settings.google_tag_manager_id

        if settings.social_links:
            form.twitter.data = settings.social_links.get('twitter')
            form.facebook.data = settings.social_links.get('facebook')
            form.linkedin.data = settings.social_links.get('linkedin')
            form.instagram.data = settings.social_links.get('instagram')
    
    return render_template('admin/settings.html', form=form, settings=settings)

# ============ NEWSLETTER MANAGEMENT ============

@admin_bp.route('/newsletter')
@admin_required
def newsletter_list():
    newsletters = Newsletter.query.order_by(Newsletter.created_at.desc()).all()
    return render_template('admin/newsletter/list.html', newsletters=newsletters)


@admin_bp.route('/newsletter/create', methods=['GET', 'POST'])
@admin_required
def newsletter_create():
    form = NewsletterForm()
    if form.validate_on_submit():
        featured_image_path = save_upload_file(form.featured_image.data, "newsletter") if form.featured_image.data else None

        newsletter = Newsletter(
            title=form.title.data,
            slug=form.slug.data,
            excerpt=form.excerpt.data,
            google_drive_link=form.google_drive_link.data,
            featured_image=featured_image_path,
            is_published=form.is_published.data,
            published_at=datetime.utcnow() if form.is_published.data else None
        )
        db.session.add(newsletter)
        db.session.commit()

        flash('Newsletter saved successfully!', 'success')
        return redirect(url_for('admin.newsletter_list'))

    return render_template('admin/newsletter/form.html', form=form, action='Create')


@admin_bp.route('/newsletter/<int:nl_id>/edit', methods=['GET', 'POST'])
@admin_required
def newsletter_edit(nl_id):
    newsletter = Newsletter.query.get_or_404(nl_id)
    form = NewsletterForm()

    if form.validate_on_submit():
        if form.featured_image.data:
            newsletter.featured_image = save_upload_file(form.featured_image.data, "newsletter")

        newsletter.title = form.title.data
        newsletter.slug = form.slug.data
        newsletter.excerpt = form.excerpt.data
        newsletter.google_drive_link = form.google_drive_link.data
        newsletter.is_published = form.is_published.data

        if form.is_published.data and not newsletter.published_at:
            newsletter.published_at = datetime.utcnow()

        db.session.commit()
        flash('Newsletter updated!', 'success')
        return redirect(url_for('admin.newsletter_list'))

    # Pre-fill
    form.title.data = newsletter.title
    form.slug.data = newsletter.slug
    form.excerpt.data = newsletter.excerpt
    form.google_drive_link.data = newsletter.google_drive_link
    form.is_published.data = newsletter.is_published

    return render_template('admin/newsletter/form.html', form=form, action='Edit', newsletter=newsletter)


@admin_bp.route('/newsletter/<int:nl_id>/delete', methods=['POST'])
@admin_required
def newsletter_delete(nl_id):
    nl = Newsletter.query.get_or_404(nl_id)
    db.session.delete(nl)
    db.session.commit()
    flash('Newsletter deleted.', 'success')
    return redirect(url_for('admin.newsletter_list'))


# ============ SEND NEWSLETTER ============

@admin_bp.route('/newsletter/send', methods=['GET', 'POST'])
@admin_required
def newsletter_send():
    """General Send Newsletter Page"""
    form = NewsletterCampaignForm()
    form.newsletter_id.choices = [(n.id, n.title) for n in Newsletter.query.order_by(Newsletter.title).all()]

    if form.validate_on_submit():
        newsletter = Newsletter.query.get_or_404(form.newsletter_id.data)
        subscribers = Subscriber.query.filter_by(is_active=True).all()

        if not subscribers:
            flash('No active subscribers found.', 'warning')
            return redirect(url_for('admin.newsletter_send'))

        newsletter_url = url_for('public.newsletter_detail', slug=newsletter.slug, _external=True)

        success_count = 0
        for sub in subscribers:
            if send_newsletter_email(
                form.subject.data or newsletter.title,
                newsletter.excerpt or '',
                sub.email,
                newsletter_url
            ):
                success_count += 1

        # Record campaign
        campaign = NewsletterCampaign(
            newsletter_id=newsletter.id,
            subject=form.subject.data or newsletter.title,
            sent_count=success_count,
            is_sent=True,
            sent_at=datetime.utcnow()
        )
        db.session.add(campaign)
        db.session.commit()

        flash(f'Newsletter sent successfully to {success_count} subscribers!', 'success')
        return redirect(url_for('admin.newsletter_sent'))

    return render_template('admin/newsletter/send.html', form=form)


@admin_bp.route('/newsletter/<int:nl_id>/send', methods=['POST'])
@admin_required
def newsletter_quick_send(nl_id):
    """Quick Send from Newsletter List (AJAX)"""
    newsletter = Newsletter.query.get_or_404(nl_id)
    subscribers = Subscriber.query.filter_by(is_active=True).all()

    if not subscribers:
        return jsonify({'success': False, 'message': 'No active subscribers'}), 400

    newsletter_url = url_for('public.newsletter_detail', slug=newsletter.slug, _external=True)

    success_count = 0
    for sub in subscribers:
        if send_newsletter_email(
            newsletter.title,
            newsletter.excerpt or '',
            sub.email,
            newsletter_url
        ):
            success_count += 1

    campaign = NewsletterCampaign(
        newsletter_id=newsletter.id,
        subject=newsletter.title,
        sent_count=success_count,
        is_sent=True,
        sent_at=datetime.utcnow()
    )
    db.session.add(campaign)
    db.session.commit()

    return jsonify({
        'success': True, 
        'message': f'Sent to {success_count} subscribers!'
    })


@admin_bp.route('/newsletter/sent')
@admin_required
def newsletter_sent():
    campaigns = NewsletterCampaign.query.order_by(NewsletterCampaign.sent_at.desc()).all()
    return render_template('admin/newsletter/sent.html', campaigns=campaigns)

@admin_bp.route('/subscribers')
@admin_required
def subscribers_list():
    """List all subscribers"""
    page = request.args.get('page', 1, type=int)
    subscribers = Subscriber.query.order_by(Subscriber.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('admin/subscribers/list.html', subscribers=subscribers)


@admin_bp.route('/subscribers/<int:subscriber_id>/delete', methods=['POST'])
@admin_required
def subscriber_delete(subscriber_id):
    """Delete subscriber"""
    subscriber = Subscriber.query.get_or_404(subscriber_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            db.session.delete(subscriber)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Subscriber removed.'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    
    db.session.delete(subscriber)
    db.session.commit()
    flash('Subscriber removed.', 'success')
    return redirect(url_for('admin.subscribers_list'))


def url_has_allowed_host_and_scheme(target):
    """Validate redirect target"""

    if not target:
        return False

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return (
        test_url.scheme in ('http', 'https')
        and ref_url.netloc == test_url.netloc
    )

# ============ HERO CAROUSEL MANAGEMENT ============

@admin_bp.route('/hero-slides')
@admin_required
def hero_slides_list():
    slides = HeroSlide.query.order_by(HeroSlide.order).all()
    return render_template('admin/hero_slides/list.html', slides=slides)


@admin_bp.route('/hero-slides/create', methods=['GET', 'POST'])
@admin_required
def hero_slide_create():
    form = HeroSlideForm()
    
    if form.validate_on_submit():
        image_path = None
        if form.image.data:
            image_path = save_upload_file(form.image.data, "hero")
        
        if not image_path:
            flash('Image is required.', 'danger')
            return render_template('admin/hero_slides/form.html', form=form, action='Create')

        slide = HeroSlide(
            title=form.title.data,
            subtitle=form.subtitle.data,
            btn_text=form.btn_text.data,
            btn_url=form.btn_url.data,
            alt_text=form.alt_text.data,
            image_path=image_path,
            order=form.order.data or 0,
            is_active=form.is_active.data
        )
        db.session.add(slide)
        db.session.commit()
        
        flash('Hero slide created successfully!', 'success')
        return redirect(url_for('admin.hero_slides_list'))
    
    return render_template('admin/hero_slides/form.html', form=form, action='Create')


@admin_bp.route('/hero-slides/<int:slide_id>/edit', methods=['GET', 'POST'])
@admin_required
def hero_slide_edit(slide_id):
    slide = HeroSlide.query.get_or_404(slide_id)
    form = HeroSlideForm()
    
    if form.validate_on_submit():
        if form.image.data:
            image_path = save_upload_file(form.image.data, "hero")
            if image_path:
                slide.image_path = image_path
        
        slide.title = form.title.data
        slide.subtitle = form.subtitle.data
        slide.btn_text = form.btn_text.data
        slide.btn_url = form.btn_url.data
        slide.alt_text = form.alt_text.data
        slide.order = form.order.data or 0
        slide.is_active = form.is_active.data
        
        db.session.commit()
        flash('Hero slide updated successfully!', 'success')
        return redirect(url_for('admin.hero_slides_list'))
    
    # Pre-fill form
    form.title.data = slide.title
    form.subtitle.data = slide.subtitle
    form.btn_text.data = slide.btn_text
    form.btn_url.data = slide.btn_url
    form.alt_text.data = slide.alt_text
    form.order.data = slide.order
    form.is_active.data = slide.is_active
    
    return render_template('admin/hero_slides/form.html', 
                         form=form, 
                         action='Edit', 
                         slide=slide)


@admin_bp.route('/hero-slides/<int:slide_id>/delete', methods=['POST'])
@admin_required
def hero_slide_delete(slide_id):
    slide = HeroSlide.query.get_or_404(slide_id)
    
    # Delete physical image file if it exists
    if slide.image_path:
        try:
            # Remove leading slash if present
            file_path = slide.image_path.lstrip('/')
            full_path = os.path.join(current_app.root_path, file_path)
            
            if os.path.exists(full_path):
                os.remove(full_path)
                print(f"Deleted image file: {full_path}")
        except Exception as e:
            print(f"Warning: Could not delete image file: {e}")
            # Continue anyway - we still want to delete the DB record
    
    # Delete from database
    db.session.delete(slide)
    db.session.commit()
    
    flash('Hero slide and associated image deleted successfully.', 'success')
    return redirect(url_for('admin.hero_slides_list'))


# ==================== ADMIN REGISTRATION ====================

@admin_bp.route('/register', methods=['GET', 'POST'])
@admin_required
def register_admin():
    form = AdminRegisterForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower()
        
        user = User(
            username=form.username.data.strip(),
            first_name=form.first_name.data.strip() if form.first_name.data else '',
            last_name=form.last_name.data.strip() if form.last_name.data else '',
            email=email,
            is_admin=True,
            is_active=False
        )
        token = user.generate_activation_token()
        
        db.session.add(user)
        db.session.commit()

        send_activation_email(user, token)
        
        flash(f'Invitation sent to {email}. They will receive an email to set their password.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/register.html', form=form)


# ============ ADMIN USER MANAGEMENT ============

@admin_bp.route('/admins')
@admin_required
def admins_list():
    """List all admins except current user"""
    admins = User.query.filter(
        User.id != current_user.id,
        User.is_admin == True
    ).order_by(User.created_at.desc()).all()
    
    return render_template('admin/admins/list.html', admins=admins)

@admin_bp.route('/admins/create', methods=['GET', 'POST'])
@admin_required
def admin_create():
    form = AdminRegisterForm()

    print("Request method:", request.method)

    if form.validate_on_submit():
        print("Form validated")

        try:
            print("Creating user...")

            user = User(
                username=form.username.data.strip(),
                first_name=form.first_name.data.strip() if form.first_name.data else '',
                last_name=form.last_name.data.strip() if form.last_name.data else '',
                email=form.email.data.strip().lower(),
                is_admin=True,
                is_active=False
            )

            token = user.generate_activation_token()

            db.session.add(user)
            db.session.commit()

            print("User saved")

            send_activation_email(user, token)

            print("Email sent")

            flash(
                f'New admin account created and invitation sent to {user.email}',
                'success'
            )

            return redirect(url_for('admin.admins_list'))

        except Exception as e:
            db.session.rollback()
            print("ERROR:", str(e))
            flash(str(e), 'danger')

    else:
        print("Form errors:", form.errors)

    return render_template(
        'admin/admins/form.html',
        form=form,
        action='Create'
    )


@admin_bp.route('/admins/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot edit your own account here.", "warning")
        return redirect(url_for('admin.admins_list'))
    
    form = AdminRegisterForm()
    
    if form.validate_on_submit():
        user.username = form.username.data.strip()
        user.first_name = form.first_name.data.strip() if form.first_name.data else ''
        user.last_name = form.last_name.data.strip() if form.last_name.data else ''
        user.email = form.email.data.strip().lower()
        
        db.session.commit()
        flash('Admin updated successfully!', 'success')
        return redirect(url_for('admin.admins_list'))
    
    # Pre-fill
    form.username.data = user.username
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.email.data = user.email
    
    return render_template('admin/admins/form.html', form=form, action='Edit', user=user)


@admin_bp.route('/admins/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found."
        }), 404

    if user.id == current_user.id:
        return jsonify({
            "success": False,
            "message": "You cannot delete your own account!"
        }), 400

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Admin account deleted successfully."
    }), 200


# ====================    ====================
@admin_bp.route('/testimonials/links')
@admin_required
def testimonial_links():
    submissions = TestimonialSubmission.query.order_by(TestimonialSubmission.created_at.desc()).all()
    return render_template('admin/testimonials/links.html', submissions=submissions)


@admin_bp.route('/testimonials/generate-link', methods=['GET', 'POST'])
@admin_required
def generate_testimonial_link():
    form = TestimonialLinkForm()
    if form.validate_on_submit():
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=form.expires_in_days.data)

        submission = TestimonialSubmission(
            token=token,
            client_name=form.client_name.data,
            client_company=form.client_company.data,
            email=form.email.data,
            expires_at=expires_at
        )
        db.session.add(submission)
        db.session.commit()

        submission_url = url_for('public.submit_testimonial', token=token, _external=True)
        send_testimonial_invite_email(submission, submission_url)

        flash('Testimonial link generated and sent!', 'success')
        return redirect(url_for('admin.testimonial_links'))

    return render_template('admin/testimonials/generate_link.html', form=form)


@admin_bp.route('/testimonials/links/<int:sub_id>/resend', methods=['POST'])
@admin_required
def resend_testimonial_link(sub_id):
    submission = TestimonialSubmission.query.get_or_404(sub_id)
    
    if submission.is_used:
        return jsonify({'success': False, 'message': 'This link has already been used.'})
    
    # Regenerate token and extend expiry by 7 days
    submission.token = secrets.token_urlsafe(32)
    submission.expires_at = datetime.utcnow() + timedelta(days=7)
    db.session.commit()
    
    submission_url = url_for('public.submit_testimonial', token=submission.token, _external=True)
    
    send_testimonial_invite_email(submission, submission_url)
    
    return jsonify({
        'success': True, 
        'message': 'Testimonial link has been resent successfully!'
    })

@admin_bp.route('/testimonials/<int:testimonial_id>/approve', methods=['POST'])
@admin_required
def testimonial_approve(testimonial_id):
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    testimonial.is_active = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Testimonial approved and published on the website.'
    })


@admin_bp.route('/testimonials/<int:testimonial_id>/delete', methods=['POST'])
@admin_required
def testimonial_delete(testimonial_id):
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    db.session.delete(testimonial)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Testimonial deleted.'})
    
    flash('Testimonial deleted successfully.', 'success')
    return redirect(url_for('admin.testimonials_list'))

@admin_bp.route('/testimonials/links/<int:sub_id>/delete', methods=['POST'])
@admin_required
def testimonial_link_delete(sub_id):
    """Delete a testimonial submission link"""
    submission = TestimonialSubmission.query.get_or_404(sub_id)
    
    db.session.delete(submission)
    db.session.commit()
    
    flash('Testimonial submission link deleted successfully.', 'success')
    return redirect(url_for('admin.testimonial_links'))
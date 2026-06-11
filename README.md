# John & Eniola Financial Consultancy Website

A fully responsive, production-ready financial consultancy website built with Flask, MySQL, and TailwindCSS. Features a dynamic admin dashboard for complete content management.

## Features

- **Responsive Design**: Mobile-first design
- **Dynamic Content**: Full CMS with admin dashboard
- **Blog System**: Create/edit/delete posts with categories and tags
- **Comment Moderation**: Nested comments with admin approval workflow
- **Newsletter System**: Email subscriptions and campaign management
- **Service Management**: Manage services with key features and descriptions
- **Team Management**: Showcase team members with bios and contact info
- **Contact Form**: AJAX-enabled contact form with email notifications
- **Admin Dashboard**: Complete control panel for managing all content
- **CSRF Protection**: Flask-WTF forms with built-in security
- **Email Integration**: Flask-Mail support for transactional and newsletter emails

## Tech Stack

- **Frontend**: HTML5, TailwindCSS v4, Vanilla JavaScript with AJAX
- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: MySQL with PyMySQL driver
- **Forms**: Flask-WTF with WTForms validation
- **Email**: Flask-Mail with SMTP (Gmail/SendGrid compatible)
- **Authentication**: Flask-Login with secure password hashing

## Installation & Setup

### 1. Create Virtual Environment

```bash
cd /je-rebuild
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and update with your settings:

```env
SECRET_KEY=your-secure-secret-key
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=john_eniola_consultancy
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@johneniola.com
```

### 4. Initialize Database

```bash
python init_db.py
```

This will:
- Create all database tables
- Create an admin user (username: `admin`, password: `admin123`)
- Populate sample services data

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Admin Dashboard

Access the admin dashboard at `http://localhost:5000/admin`

### Admin Features

- **Dashboard**: Overview of blog posts, services, team members, subscribers, and comments
- **Blog Management**: Create, edit, delete blog posts with featured images
- **Service Management**: Manage your service offerings with detailed descriptions
- **Team Management**: Add and manage team members with profiles
- **Testimonials**: Create and manage client testimonials
- **Comment Moderation**: Review and approve comments on blog posts
- **Newsletter System**: Create and send newsletters to subscribers
- **Subscriber Management**: View and manage newsletter subscribers
- **Site Settings**: Update company information, logos, contact details, and social links

## File Structure

```
project/
├── app.py                    # Flask application factory
├── models.py                # Database models
├── forms.py                  # Flask-WTF form definitions
├── init_db.py               # Database initialization script
├── routes/
│   ├── public_routes.py      # Public-facing routes
│   └── admin_routes.py       # Admin dashboard routes
├── templates/
│   ├── base.html             # Base template
│   ├── public/               # Public page templates
│   │   ├── home.html
│   │   ├── about.html
│   │   ├── services.html
│   │   ├── insights.html
│   │   ├── blog-detail.html
│   │   ├── contact.html
│   │   ├── navbar.html
│   │   ├── footer.html
│   │   ├── 404.html
│   │   └── 500.html
│   └── admin/                # Admin templates
│       ├── base.html
│       ├── login.html
│       └── dashboard.html
├── static/
│   ├── css/                  # Compiled CSS
│   ├── js/
│   │   └── main.js          # JavaScript utilities
│   ├── images/              # Image assets
│   └── uploads/             # User uploads
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Database Models

- **User**: Admin user accounts with password hashing
- **SiteSettings**: Global site configuration (company info, logos, contact details)
- **Service**: Service offerings with descriptions and features
- **BlogPost**: Blog articles with tags, categories, and featured images
- **Comment**: Nested comments with moderation system
- **Testimonial**: Client testimonials with ratings
- **TeamMember**: Team member profiles
- **Subscriber**: Newsletter subscribers
- **Newsletter**: Newsletter campaigns
- **Media**: Uploaded file management

## Email Configuration

### Gmail Setup

1. Enable 2-Factor Authentication on your Google Account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the app password in `MAIL_PASSWORD`

### SendGrid Setup

Replace mail configuration with SendGrid SMTP:
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

## Security Considerations

- All forms include CSRF protection via Flask-WTF
- Passwords are hashed using Werkzeug's security functions
- SQL injection is prevented through SQLAlchemy ORM
- User input is sanitized using Bleach library
- Admin routes require authentication and authorization
- File uploads are validated for type and size

## Design Features

- **Color Scheme**: Navy blue (#001A4D) primary with orange (#ff6b35) accents
- **Typography**: Modern sans-serif fonts with clear hierarchy
- **Responsive Grid**: Mobile-first flexbox/grid layouts
- **Smooth Animations**: CSS transitions and hover effects
- **Card-based Design**: Consistent component styling
- **Accessibility**: Semantic HTML with ARIA labels

## API Endpoints

### Public Routes

- `GET /` - Home page
- `GET /about` - About page
- `GET /services` - Services page
- `GET /insights` - Blog listing page
- `GET /insights/<slug>` - Blog detail page
- `POST /insights/<slug>` - Submit blog comment (AJAX)
- `GET /contact` - Contact page
- `POST /contact` - Submit contact form (AJAX)
- `POST /newsletter/subscribe` - Subscribe to newsletter (AJAX)

### Admin Routes

- `GET /admin/login` - Admin login
- `POST /admin/login` - Process login
- `GET /admin/logout` - Logout
- `GET /admin/` - Dashboard
- `GET /admin/blog` - Blog list
- `GET /admin/blog/create` - Create blog post
- `POST /admin/blog/create` - Save new post
- `GET /admin/blog/<id>/edit` - Edit blog post
- `POST /admin/blog/<id>/edit` - Update post
- `POST /admin/blog/<id>/delete` - Delete post
- Similar endpoints for: services, team, testimonials, comments, settings, newsletter, subscribers

## Troubleshooting

### Database Connection Error

- Ensure MySQL is running
- Check database credentials in `.env`
- Verify database exists: `CREATE DATABASE john_eniola_consultancy;`

### Email Not Sending

- Check SMTP credentials in `.env`
- Enable "Less secure app access" for Gmail (if not using app passwords)
- Check email logs in console for specific errors
- Test with a simple SMTP connection

### Static Files Not Loading

- Ensure TailwindCSS CDN is available (requires internet)
- Check static folder path in app.py
- Clear browser cache

## Customization

### Change Color Scheme

Edit the color variables in `templates/base.html`:

```css
:root {
    --color-primary: #001A4D;  /* Change this */
    --color-accent: #ff6b35;    /* And this */
}
```

### Add New Pages

1. Create route in `routes/public_routes.py`
2. Create template in `templates/public/`
3. Add navigation link in `templates/public/navbar.html`

### Extend Forms

1. Add form class in `forms.py` with WTForms validators
2. Create template with form fields
3. Add route in appropriate `routes/` file

## Performance Optimization

- Database queries are optimized with proper indexing
- Images should be compressed before upload
- Static files are served with cache headers
- Pagination limits blog queries to 6 posts per page
- Lazy loading for images where applicable

## Deployment

### To Vercel (Next.js not compatible)

This is a Flask application and should be deployed to:
- Heroku
- PythonAnywhere
- DigitalOcean
- AWS EC2
- Railway
- Render

### Environment Variables

Set these in your hosting platform:
- All variables from `.env` file
- Ensure `SECRET_KEY` is a strong random value
- Update database credentials for production database

## License

Created for John & Eniola Consultancy - 2026

## Support

For questions or issues, contact: info@johneniola.com

---

**Built with ❤️ for Financial Excellence**

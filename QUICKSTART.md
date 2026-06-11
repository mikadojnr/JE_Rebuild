# Quick Start Guide

Get the John & Eniola Consultancy website running in 5 minutes.

## Prerequisites

- Python 3.8+
- MySQL 5.7+
- Git

## 1-Minute Setup (Linux/Mac)

```bash
# Navigate to project directory
cd /vercel/share/v0-project

# Run startup script
chmod +x startup.sh
./startup.sh
```

## Windows Setup (2 Minutes)

```cmd
# Open Command Prompt in project directory
cd \path\to\v0-project

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy content from .env.example and save as .env
copy .env.example .env
# Edit .env with your settings

# Initialize database
python init_db.py

# Run application
python app.py
```

## Manual Setup (3 Steps)

### Step 1: Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Environment
Create `.env` file:
```env
SECRET_KEY=your-secret-key-here
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=john_eniola_consultancy
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Step 3: Run Application
```bash
python init_db.py
python app.py
```

## Access the Application

- **Website**: http://localhost:5000
- **Admin Dashboard**: http://localhost:5000/admin
- **Username**: admin
- **Password**: admin123

## Verify Everything Works

1. Visit http://localhost:5000 - You should see the home page
2. Go to http://localhost:5000/admin - Admin login page should appear
3. Login with admin/admin123
4. Check Dashboard - Should show stats

## Next: Configuration

### Update Site Info
1. Login to admin dashboard
2. Go to Settings
3. Update company name, phone, email, address
4. Upload your logo
5. Add social media links

### Create Content
- **Blog Posts**: Go to Blog Posts → Create Post
- **Services**: Go to Services → Add Service  
- **Team**: Go to Team Members → Add Member
- **Testimonials**: Go to Testimonials → Add Testimonial

### Email Setup (Important!)

For contact form and newsletter to work:

**Gmail:**
1. Enable 2-Factor Authentication
2. Visit https://myaccount.google.com/apppasswords
3. Generate app password
4. Paste into `.env` MAIL_PASSWORD

**SendGrid (or other SMTP):**
Update MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD in `.env`

## Troubleshooting

### Port 5000 Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
export FLASK_RUN_PORT=5001
```

### Database Connection Error
```bash
# Check MySQL is running
mysql -u root -p

# Create database if not exists
CREATE DATABASE john_eniola_consultancy;

# Re-run initialization
python init_db.py
```

### Email Not Sending
- Verify MAIL_USERNAME and MAIL_PASSWORD in .env
- Check firewall allows port 587
- Ensure 2FA is enabled (Gmail)
- Use app-specific password (Gmail)

### Dependencies Install Failed
```bash
# Upgrade pip first
pip install --upgrade pip

# Install one by one
pip install flask
pip install flask-sqlalchemy
# ... etc
```

## Project Structure

```
project/
├── app.py                 # Main application
├── models.py              # Database models
├── forms.py               # Flask-WTF forms
├── init_db.py            # Database initialization
├── routes/
│   ├── public_routes.py   # Public pages
│   └── admin_routes.py    # Admin dashboard
├── templates/
│   ├── public/            # Public page templates
│   └── admin/             # Admin dashboard templates
├── static/
│   ├── js/                # JavaScript files
│   ├── images/            # Static images
│   └── uploads/           # User uploaded files
├── .env                   # Environment variables
└── requirements.txt       # Python dependencies
```

## Common Tasks

### Change Admin Password
1. Login to admin dashboard
2. In database: UPDATE users SET password_hash='...' WHERE id=1
3. Or use admin panel (if password change feature added)

### Backup Database
```bash
mysqldump -u root -p john_eniola_consultancy > backup.sql
```

### Restore from Backup
```bash
mysql -u root -p john_eniola_consultancy < backup.sql
```

### Export Blog Posts
Database includes all posts in `blog_posts` table, exportable as CSV

### Update Site Logo
1. Login to admin
2. Go to Settings
3. Upload new logo under "Logo & Branding"
4. Save - Logo updates immediately

## Development Tips

### Enable Debug Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Clear Database & Start Fresh
```bash
# Drop database
mysql -u root -p -e "DROP DATABASE john_eniola_consultancy;"

# Re-initialize
python init_db.py
```

### View Database Tables
```bash
mysql -u root -p john_eniola_consultancy
SHOW TABLES;
DESC blog_posts;  # View table structure
SELECT * FROM users;  # View user data
```

### Add Dummy Data
Edit `init_db.py` to add sample blog posts, testimonials, etc.

## Common Errors & Fixes

| Error | Solution |
|-------|----------|
| "No module named flask" | Run: pip install -r requirements.txt |
| "Can't connect to MySQL" | Ensure MySQL running, check credentials |
| "Port 5000 in use" | Kill process or use different port |
| "Template not found" | Check templates/ directory exists |
| "Module 'app' not found" | Run from project root directory |

## Moving to Production

Once verified locally:

1. Read DEPLOYMENT.md for hosting options
2. Set strong SECRET_KEY
3. Change admin password
4. Configure production database
5. Set up automated backups
6. Enable HTTPS
7. Monitor application logs

## Support

- **Docs**: Read README.md for complete documentation
- **Deployment**: See DEPLOYMENT.md for hosting guides
- **Checklist**: Review CHECKLIST.md for implementation details

## What's Working Out of the Box

✅ All 6 public pages (Home, About, Services, Insights, Blog Detail, Contact)
✅ Full admin dashboard with content management
✅ Blog posting and comment system
✅ Contact form with email notifications
✅ Newsletter subscription system
✅ Team member profiles
✅ Service showcase
✅ Testimonials display
✅ Fully responsive design
✅ AJAX form submissions
✅ Database with 10 models
✅ Authentication and security

## Next Steps

1. **Customize Design**: Edit colors in `templates/base.html`
2. **Add Content**: Use admin dashboard to create posts/services
3. **Configure Email**: Set up SMTP for working contact forms
4. **Upload Logo**: Add company logo via admin settings
5. **Deploy**: Follow DEPLOYMENT.md for hosting

---

**Your financial consultancy website is ready to go!**

Start with: `python app.py` then visit http://localhost:5000

# Deployment Guide - John & Eniola Consultancy

## Quick Start

### Windows Users

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file (copy from .env.example)

# 4. Initialize database
python init_db.py

# 5. Run application
python app.py
```

### Linux/Mac Users

```bash
# 1. Run startup script (recommended)
chmod +x startup.sh
./startup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python app.py
```

## Configuration

### Environment Variables (.env)

Create a `.env` file in the project root with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-very-secure-random-string-here-minimum-32-chars

# Database Configuration
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=john_eniola_consultancy

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_DEFAULT_SENDER=noreply@johneniola.com
```

### Database Setup

Before running the application, ensure MySQL is running:

```bash
# Create database
mysql -u root -p
CREATE DATABASE john_eniola_consultancy;
EXIT;

# Initialize tables and admin user
python init_db.py
```

Default admin credentials:
- Username: `admin`
- Password: `admin123`
- Email: `admin@johneniola.com`

**IMPORTANT:** Change these credentials immediately after first login!

## Gmail Configuration for Email

1. Go to https://myaccount.google.com
2. Enable 2-Factor Authentication
3. Go to https://myaccount.google.com/apppasswords
4. Generate app password for "Mail"
5. Copy the 16-character password to `MAIL_PASSWORD` in .env

## Production Deployment

### Heroku

1. Install Heroku CLI
2. Create `Procfile`:
```
web: python app.py
```

3. Create `runtime.txt`:
```
python-3.11.7
```

4. Deploy:
```bash
heroku login
heroku create your-app-name
git push heroku main
heroku config:set SECRET_KEY=your-secret
heroku config:set DB_HOST=your-db-host
# ... set all environment variables
heroku run python init_db.py
```

### PythonAnywhere

1. Sign up at pythonanywhere.com
2. Upload project files
3. Create virtual environment
4. Set up web app with Flask
5. Configure environment variables in web app settings
6. Run `python init_db.py` in bash console
7. Reload web app

### DigitalOcean / AWS / Azure

1. Create Ubuntu server (18.04 LTS or newer)
2. SSH into server
3. Install Python, MySQL, Nginx
4. Clone repository
5. Set up virtual environment
6. Create systemd service file
7. Configure Nginx as reverse proxy
8. Get SSL certificate (Let's Encrypt)

**Example Systemd Service:**
```ini
[Unit]
Description=John & Eniola Consultancy
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/john-eniola
ExecStart=/var/www/john-eniola/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENV FLASK_APP=app.py
EXPOSE 5000

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t john-eniola .
docker run -p 5000:5000 --env-file .env john-eniola
```

## Performance Optimization

### Database Optimization

1. Add indexes on frequently queried columns:
```sql
CREATE INDEX idx_blog_published ON blog_posts(is_published);
CREATE INDEX idx_comment_approved ON comments(is_approved);
CREATE INDEX idx_subscriber_email ON subscribers(email);
```

2. Enable query caching in MySQL config

### Application Optimization

1. Enable gzip compression in Nginx
2. Use CDN for static files
3. Implement caching headers
4. Minify CSS/JavaScript
5. Optimize images before upload

### Monitoring

Install monitoring tools:
- **Sentry** for error tracking
- **New Relic** for performance monitoring
- **Uptime Robot** for uptime monitoring

## Security Checklist

Before going live:

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Change default admin password
- [ ] Enable HTTPS/SSL certificate
- [ ] Set `FLASK_ENV=production`
- [ ] Disable Flask debug mode
- [ ] Sanitize all user inputs
- [ ] Enable CORS only for trusted domains
- [ ] Set strong database password
- [ ] Enable database backups
- [ ] Configure firewall rules
- [ ] Keep dependencies updated
- [ ] Regular security audits

## Backup & Recovery

### Database Backup

```bash
# Manual backup
mysqldump -u root -p john_eniola_consultancy > backup.sql

# Restore from backup
mysql -u root -p john_eniola_consultancy < backup.sql
```

### File Backups

Backup these directories regularly:
- `static/uploads/` (user uploaded files)
- `.env` (environment variables - NEVER commit)
- Database daily

### Automated Backups (Recommended)

Use cron job for daily backups:
```bash
0 2 * * * /home/user/backup-script.sh
```

## Troubleshooting

### Database Connection Issues

```bash
# Check MySQL is running
mysql -u root -p -e "SELECT 1"

# Check database exists
mysql -u root -p -e "SHOW DATABASES"

# Check user permissions
mysql -u root -p -e "SHOW GRANTS FOR 'root'@'localhost'"
```

### Email Not Sending

1. Check SMTP credentials in .env
2. Verify 2FA is enabled on Gmail
3. Use app-specific password
4. Check firewall allows port 587
5. Review email logs: `tail -f logs/email.log`

### Static Files Not Loading

1. Check `static/` directory exists
2. Verify file permissions: `chmod 755 static/`
3. Clear browser cache
4. In production, configure Nginx to serve static files

### High Memory Usage

1. Check for infinite loops in routes
2. Implement pagination for large datasets
3. Use database connection pooling
4. Monitor with: `ps aux | grep python`

## Maintenance

### Regular Tasks

- **Daily**: Monitor error logs, check system health
- **Weekly**: Review analytics, check backups
- **Monthly**: Update dependencies, security audit
- **Quarterly**: Database optimization, performance review
- **Annually**: Full security audit, disaster recovery test

### Update Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update all packages
pip install -r requirements.txt --upgrade
```

## Support & Debugging

### Enable Debug Mode (Development Only)

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### View Application Logs

```bash
# If running with systemd
journalctl -u john-eniola -f

# If running in terminal
# See console output directly
```

### Database Queries Debug

Add to app.py:
```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## Performance Benchmarks

Expected performance (with optimizations):
- Page load time: < 1 second
- Database queries: < 100ms average
- Concurrent users: 500+ (with proper hosting)
- Uptime: 99.9%+ (with proper infrastructure)

## Contact & Support

For deployment issues: info@johneniola.com

---

**Last Updated:** May 2026  
**Version:** 1.0.0

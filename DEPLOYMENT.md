# SoulOS Django Deployment Guide

## 1. Configure Static Files (`soulos/settings.py`)

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com', 'localhost', '127.0.0.1']
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
```

Run collectstatic locally:

```bash
python manage.py collectstatic
```

## 2. Push Code to GitHub

```bash
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

## 3. Clone Repository on PythonAnywhere

```bash
# Use PythonAnywhere Bash console or SSH
cd ~
git clone https://github.com/YOUR_USERNAME/soulos.git
cd soulos
```

## 4. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # For WSGI
```

## 5. Configure WSGI File

Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:

```python
import os
import sys

# Add project directory to path
path = '/home/yourusername/soulos'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'soulos.settings'
os.environ['SECRET_KEY'] = 'your-secret-key-here'
os.environ['DEBUG'] = 'False'

# Activate virtual environment
activate_this = '/home/yourusername/soulos/venv/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 6. Set Environment Variables

In PythonAnywhere Web tab → Environment variables:
- `DJANGO_SETTINGS_MODULE` = `soulos.settings`
- `SECRET_KEY` = `your-django-secret-key`
- `DEBUG` = `False`

Or in WSGI file as shown above.

## 7. Configure Static Files in PythonAnywhere

In PythonAnywhere Web tab → Static files section:
- URL: `/static/`
- Directory: `/home/yourusername/soulos/staticfiles`

## 8. Initialize Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

## 9. Reload Web App

In PythonAnywhere Web tab → Click **Reload** button

Verify at: `https://yourusername.pythonanywhere.com`

## 10. Post-Deployment Workflow

When you make local changes:

```bash
# 1. Edit code locally, test with DEBUG=True

# 2. Commit and push to GitHub
git add .
git commit -m "Update feature X"
git push origin main

# 3. SSH into PythonAnywhere or use Bash console
cd ~/soulos
git pull origin main
source venv/bin/activate

# 4. Apply database migrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Reload web app in PythonAnywhere dashboard
```

## 11. Professional Deployment Checklist

### Security
- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` set via environment variable
- [ ] `ALLOWED_HOSTS` configured with domain
- [ ] HTTPS enabled in PythonAnywhere Web tab
- [ ] Database credentials in environment variables
- [ ] `SECURE_SSL_REDIRECT = True` in production
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`

### Mobile Responsiveness
- [ ] Test all pages on mobile viewport (375px, 768px)
- [ ] Ensure forms are touch-friendly (min 44px tap targets)
- [ ] Verify CSS is responsive with media queries
- [ ] Test transformation log on mobile
- [ ] Verify buttons and links are easily tappable

### Scalability
- [ ] Use PostgreSQL for production database (not SQLite)
- [ ] Configure `CACHES` with Redis or Memcached
- [ ] Set up logging with `LOGGING` config in settings
- [ ] Configure email backend for error notifications
- [ ] Use `gunicorn` or `uwsgi` as WSGI server
- [ ] Set up CI/CD with GitHub Actions
- [ ] Regular database backups
- [ ] Monitor disk space on PythonAnywhere

## 12. Monitoring & Logs

### View Django Logs

```bash
# In PythonAnywhere Bash console
tail -f ~/soulos/logs/django.log
```

### Configure Logging in `soulos/settings.py`

```python
import os
from pathlib import Path

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'Core_healing_path': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Create logs directory
Path(BASE_DIR / 'logs').mkdir(exist_ok=True)
```

### Error Handling

```python
# In settings.py
ADMINS = [('Admin Name', 'admin@example.com')]
MANAGERS = ADMINS

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

### Monitor PythonAnywhere

- Check **Web** tab for error logs
- Monitor CPU/RAM usage in **Account** tab
- Set up scheduled tasks for database backups
- Enable error notification emails in settings

## 13. Quick Reference Commands

```bash
# Local development
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic

# Production deployment
git push origin main
# Then on PythonAnywhere:
cd ~/soulos && git pull && source venv/bin/activate && python manage.py migrate && python manage.py collectstatic --noinput
# Reload in web dashboard
```

## 14. Troubleshooting

- **Static files not loading**: Verify `STATIC_ROOT` and PythonAnywhere static files mapping
- **Import errors**: Check WSGI path configuration
- **Database errors**: Run `python manage.py migrate` after pulling code
- **Permission errors**: Check file permissions in PythonAnywhere Bash
- **White screen**: Check error logs in PythonAnywhere Web tab

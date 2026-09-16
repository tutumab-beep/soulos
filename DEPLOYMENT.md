# SoulOS Deployment Guide (PythonAnywhere)

## 1. Configure `soulos/settings.py`

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "unsafe-default-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    "soulos.pythonanywhere.com",
    "127.0.0.1",
    "localhost",
    "35.173.69.207",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "system_apps.core",
    "system_apps.accounts",
    "system_apps.dashboard_app",
    "system_apps.profile_app",
    "system_apps.legal",
    "Core_healing_path",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "soulos.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "soulos.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

LOGIN_REDIRECT_URL = "dashboard_app:home"
LOGOUT_REDIRECT_URL = "index"

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}
```

## 2. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## 3. Configure WSGI File on PythonAnywhere

Create `/var/www/soulos_pythonanywhere_com_wsgi.py` on the server:

```python
import os
import sys

path = "/home/SoulOS/soulos"
if path not in sys.path:
    sys.path.append(path)

os.environ["DJANGO_SETTINGS_MODULE"] = "soulos.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Then point the PythonAnywhere **Web** tab → WSGI configuration file to this path.

## 4. Set Environment Variables (PythonAnywhere)

In the PythonAnywhere **Web** tab → **Environment variables**:

| Variable | Value |
|---|---|
| `DJANGO_SECRET_KEY` | your-secret-key |
| `DEBUG` | False |

## 5. Configure Static & Media Files in PythonAnywhere

In the **Web** tab → **Static files** section:

| URL | Directory |
|---|---|
| `/static/` | `/home/SoulOS/soulos/static/` |
| `/media/` | `/home/SoulOS/soulos/media/` |

## 6. Database

Currently using SQLite:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

Run migrations:
```bash
python manage.py migrate
```

## 7. Reload Web App

After every change, click **Reload** in the PythonAnywhere Web tab.

## 8. Verify Deployment

Visit:
- `https://soulos.pythonanywhere.com`

## Notes

- Keep `DEBUG = False` in production.
- Never commit `DJANGO_SECRET_KEY` to version control.
- Later switch to PostgreSQL for scaling.

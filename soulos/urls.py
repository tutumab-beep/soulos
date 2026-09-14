"""
URL configuration for soulos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("system_apps.core.urls")),
    path("accounts/", include("system_apps.accounts.urls")),
    path("dashboard/", include("system_apps.dashboard_app.urls")),
    path("core-healing-path/", include("Core_healing_path.urls")),
    path("profile/", include("system_apps.profile_app.urls")),
    path("legal/", include("system_apps.legal.urls")),
    path("soullog/", include("soullog.urls")),
    path("work-alignment/", include("work_alignment.urls")),
    path("soulconnect/", include("soulconnect.urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf.urls import include
from django.contrib import admin
import django
from django.urls import path

admin_urls = (admin.site.urls if (django.VERSION[0] >= 2) else include(admin.site.urls))

urlpatterns = [
    path('admin/', admin_urls),
]

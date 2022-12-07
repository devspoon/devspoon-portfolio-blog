"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from users.admin import user_admin_site
from blog.admin.blog_common_admin import blog_admin_site
from board.admin.board_common_admin import board_admin_site

error_patterns = []

admin_patterns = [
    #path('admin/', admin.site.urls),
    path('user/', user_admin_site.urls),
    path('blog/', blog_admin_site.urls),
    path('board/', board_admin_site.urls),
]

urlpatterns = [
    path('admin/', include(admin_patterns)),
    path('oauth/', include('allauth.urls')),
    path('summernote/',include('django_summernote.urls')),
    path('users/', include('users.urls')),
    path('blog/', include('blog.urls')),
    path('', include('home.urls')),
    path('board/', include('board.urls')),
    path('error/', include(error_patterns)),
]

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:

        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
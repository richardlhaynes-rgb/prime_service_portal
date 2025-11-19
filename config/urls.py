from django.contrib import admin
from django.urls import path
from core.views import home  # <--- We import our new view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # <--- The empty string means "The Homepage"
]
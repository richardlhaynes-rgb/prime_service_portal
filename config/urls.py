from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from service_desk import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('service-desk/', include('service_desk.urls')),
    path('kb/', include('knowledge_base.urls')),
    
    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
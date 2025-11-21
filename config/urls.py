from django.contrib import admin
from django.urls import path, include
from service_desk import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('service-desk/', include('service_desk.urls')),
    path('kb/', include('knowledge_base.urls')),
]
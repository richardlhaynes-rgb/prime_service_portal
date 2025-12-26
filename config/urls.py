from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from service_desk import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('service-desk/', include('service_desk.urls')),
    path('kb/', include('knowledge_base.urls')),
]

# Serve static and media files in development and production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
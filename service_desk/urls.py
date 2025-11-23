from django.urls import path
from . import views

urlpatterns = [
    # --- The Dashboard ---
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # --- Ticket Details (New) ---
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),

    # --- The Service Catalog (Grid) ---
    path('catalog/', views.service_catalog, name='service_catalog'),

    # --- Reporting Flows ---
    path('report/application/', views.report_application_issue, name='report_app_issue'),
    path('report/email/', views.report_email_issue, name='report_email_issue'),
    path('report/hardware/', views.report_hardware_issue, name='report_hardware_issue'),
    path('report/printer/', views.report_printer_issue, name='report_printer_issue'),
    path('request/software/', views.report_software_install, name='report_software_install'),
    path('report/general/', views.report_general_question, name='report_general_question'),
    path('request/vp-reset/', views.report_vp_reset, name='report_vp_reset'),
    path('request/vp-permissions/', views.report_vp_permissions, name='report_vp_permissions'),
]
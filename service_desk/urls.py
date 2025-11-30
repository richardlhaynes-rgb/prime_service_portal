from django.urls import path
from . import views

urlpatterns = [
    # --- User-Facing Ticket Submission Forms ---
    path('report/application/', views.report_application_issue, name='report_app_issue'),
    path('report/email/', views.report_email_issue, name='report_email_issue'),
    path('report/hardware/', views.report_hardware_issue, name='report_hardware_issue'),
    path('report/printer/', views.report_printer_issue, name='report_printer_issue'),
    path('request/software/', views.report_software_install, name='report_software_install'),
    path('report/general/', views.report_general_question, name='report_general_question'),
    path('request/vp-reset/', views.report_vp_reset, name='report_vp_reset'),
    path('request/vp-permissions/', views.report_vp_permissions, name='report_vp_permissions'),

    # --- Ticket Detail & Survey ---
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('survey/<int:ticket_id>/', views.ticket_survey, name='ticket_survey'),

    # --- Service Catalog ---
    path('catalog/', views.service_catalog, name='service_catalog'),

    # --- Knowledge Base (Viewer) ---
    path('kb/', views.kb_home, name='kb_home'),
    path('kb/article/<int:article_id>/', views.article_detail, name='article_detail'),

    # --- Management Hub & Manager Tools ---
    path('manager/hub/', views.management_hub, name='management_hub'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/settings/', views.admin_settings, name='admin_settings'),
    path('manager/technician/<str:name>/', views.technician_profile, name='technician_profile'),
    path('manager/csat/<str:tech_id>/', views.csat_report, name='csat_report_tech'),
    path('manager/csat/', views.csat_report, name='csat_report'),

    # --- Knowledge Base Manager & CRUD ---
    path('manager/kb/', views.kb_manager, name='kb_manager'),
    path('knowledge-base/add/', views.kb_add, name='kb_add'),
    path('knowledge-base/edit/<int:article_id>/', views.kb_edit, name='kb_edit'),
    path('knowledge-base/delete/<int:article_id>/', views.kb_delete, name='kb_delete'),
    path('knowledge-base/bulk/', views.kb_bulk_action, name='kb_bulk_action'),

    # --- System Logs (NEW) ---
    path('manager/logs/', views.system_logs, name='system_logs'),
]
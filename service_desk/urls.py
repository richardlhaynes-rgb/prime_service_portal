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
    
    # --- Ticket Detail View ---
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    
    # --- Service Catalog ---
    path('catalog/', views.service_catalog, name='service_catalog'),
    
    # --- Ticket Survey (CSAT Feedback Portal) ---
    path('survey/<int:ticket_id>/', views.ticket_survey, name='ticket_survey'),
    
    # --- Management Hub (Admin Launchpad) ---
    path('manager/hub/', views.management_hub, name='management_hub'),
    
    # --- Manager Analytics Dashboard ---
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    
    # --- CSAT Report (Technician-Specific) ---
    path('manager/csat/<str:tech_id>/', views.csat_report, name='csat_report_tech'),
    
    # --- CSAT Report (Global) ---
    path('manager/csat/', views.csat_report, name='csat_report'),
    
    # --- Admin Settings (System Health Configuration) ---
    path('manager/settings/', views.admin_settings, name='admin_settings'),
    
    # --- Technician Profile ---
    path('manager/technician/<str:name>/', views.technician_profile, name='technician_profile'),
    
    # --- Knowledge Base Manager (Bulk Edit) ---
    path('manager/kb/', views.kb_manager, name='kb_manager'),
    
    # --- Knowledge Base Editor (Add/Edit/Delete) ---
    path('knowledge-base/add/', views.kb_add, name='kb_add'),
    path('knowledge-base/edit/<int:article_id>/', views.kb_edit, name='kb_edit'),
    path('knowledge-base/delete/<int:article_id>/', views.kb_delete, name='kb_delete'),
]
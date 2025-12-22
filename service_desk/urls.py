from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- Authentication ---
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='dashboard'), name='logout'),

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
    path('kb/article/<int:pk>/status/', views.kb_update_status, name='kb_update_status'),

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

    # --- System Logs ---
    path('manager/logs/', views.system_logs, name='system_logs'),
    path('profile/settings/', views.my_profile, name='my_profile'),
    
    # --- Site Configuration (Admin Settings) ---
    path('settings/site/', views.site_configuration, name='site_configuration'),
    
    # --- KB Taxonomy Manager ---
    path('manager/settings/kb/category/add/', views.kb_category_add, name='kb_category_add'),
    path('manager/settings/kb/category/delete/<int:category_id>/', views.kb_category_delete, name='kb_category_delete'),
    path('manager/settings/kb/subcategory/add/', views.kb_subcategory_add, name='kb_subcategory_add'),
    path('manager/settings/kb/subcategory/delete/<int:subcategory_id>/', views.kb_subcategory_delete, name='kb_subcategory_delete'),
    
    # --- Custom User Management ---
    path('manager/users/', views.user_management, name='user_management'),
    path('manager/users/add/', views.user_add, name='user_add'),
    path('manager/users/edit/<int:user_id>/', views.user_edit, name='user_edit'),
]
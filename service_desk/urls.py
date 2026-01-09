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

    # --- Agent Ticket Creation (Power Form) ---
    path('agent/ticket/new/', views.agent_create_ticket, name='agent_create_ticket'),
    
    # --- HTMX Helpers (Cascading Dropdowns) ---
    path('htmx/load-types/', views.hx_load_types, name='hx_load_types'),
    path('htmx/load-subtypes/', views.hx_load_subtypes, name='hx_load_subtypes'),
    path('htmx/load-items/', views.hx_load_items, name='hx_load_items'),
    path('htmx/load-form/', views.hx_load_ticket_form, name='hx_load_ticket_form'),
    path('htmx/get-contact-info/', views.hx_get_contact_info, name='hx_get_contact_info'),
    path('htmx/search-users/', views.hx_search_users, name='hx_search_users'),

    # --- Omni-Search ---
    path('search/omni/', views.omni_search, name='omni_search'),

    # --- Ticket Registry ---
    path('registry/', views.ticket_registry, name='ticket_registry'),

    # --- Ticket Detail & Survey ---
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('survey/<int:ticket_id>/', views.ticket_survey, name='ticket_survey'),

    # --- Asset Management ---
    path('asset/<int:asset_id>/', views.asset_detail, name='asset_detail'),

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
    
    # --- NEW: Service Board Management ---
    path('manager/service-boards/', views.manage_service_boards, name='manage_service_boards'),

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

    # --- User Dossier (Read-Only) ---
    path('user/<int:user_id>/dossier/', views.user_dossier, name='user_dossier'),

    # --- Notifications ---
    path('notifications/poll/', views.get_notifications, name='get_notifications'),
    path('notifications/list/', views.notification_list, name='notification_list'),
    path('notifications/mark-read-all/', views.mark_all_read, name='mark_all_read'),
    path('notifications/history/', views.notification_history, name='notification_history'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/bulk/', views.notification_bulk_action, name='notification_bulk_action'),
    path('notifications/delete/', views.delete_notifications, name='delete_notifications'),

    # --- Dashboard Stats ---
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),

    # --- Technician Workspace (The New Grid) ---
    # UPDATED: Points to 'workspace' instead of 'kanban_board'
    path('workspace/', views.workspace, name='workspace'),
    path('workspace/update/', views.workspace_update, name='workspace_update'),
    
    # --- Ticket Quick View (Side Drawer) ---
    path('ticket/quick-view/<int:ticket_id>/', views.ticket_quick_view, name='ticket_quick_view'),
]
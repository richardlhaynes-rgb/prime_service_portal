from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.utils import timezone
from .forms import (
    ApplicationIssueForm, EmailMailboxForm, HardwareIssueForm, PrinterScannerForm,
    SoftwareInstallForm, GeneralQuestionForm, VPResetForm, VPPermissionsForm,
    TicketReplyForm, KBArticleForm
)
from .models import Ticket, Comment
from services import ticket_service
from datetime import datetime
import pytz

# --- USER DASHBOARD ---
@login_required
def dashboard(request):
    """
    Main Dashboard: Shows user's tickets with sorting capability.
    """
    sort_by = request.GET.get('sort', '-created_at')
    tickets = ticket_service.get_all_tickets(user=request.user)

    if sort_by.startswith('-'):
        reverse = True
        sort_field = sort_by[1:]
    else:
        reverse = False
        sort_field = sort_by

    if sort_field in ['id', 'title', 'ticket_type', 'status', 'priority', 'created_at']:
        def sort_key(t):
            if sort_field == 'id':
                return int(t.get('id', 0))
            return str(t.get(sort_field, '')).lower()
        tickets = sorted(tickets, key=sort_key, reverse=reverse)

    stats = ticket_service.get_ticket_stats(tickets)
    dashboard_stats = ticket_service.get_dashboard_stats()

    return render(request, 'service_desk/dashboard.html', {
        'tickets': tickets,
        'open_tickets': stats.get('open_tickets', 0),
        'resolved_tickets': stats.get('resolved_tickets', 0),
        'total_tickets': stats.get('total_tickets', 0),
        'system_health': dashboard_stats.get('system_health'),
        'current_sort': sort_by
    })


# --- SERVICE CATALOG ---
@login_required
def service_catalog(request):
    return render(request, 'service_desk/service_catalog.html')


# --- TICKET SUBMISSION FORMS ---
@login_required
def report_application_issue(request):
    if request.method == 'POST':
        form = ApplicationIssueForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            app = data['application_name']
            if app == 'Other' and data['other_application']:
                app = f'Other ({data["other_application"]})'
            title = f'[Portal] App Issue: {app} - {data["summary"]}'
            desc = f'USER REPORT:\n-----------------\nApp: {app}\nComputer: {data["computer_name"] or "Primary"}\n\nDETAILS:\n{data["description"]}'
            Ticket.objects.create(
                title=title,
                description=desc,
                ticket_type=Ticket.TicketType.APPLICATION,
                submitter=request.user,
                priority=Ticket.Priority.P3,
                status=Ticket.Status.NEW
            )
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('dashboard')
    else:
        form = ApplicationIssueForm()
    return render(request, 'service_desk/forms/application_issue.html', {'form': form})


@login_required
def report_email_issue(request):
    if request.method == 'POST':
        form = EmailMailboxForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            title = f'[Portal] Email: {data["request_type"]} - {data["summary"]}'
            desc = f'USER REPORT:\n-----------------\nType: {data["request_type"]}\nTarget: {data["mailbox_name"] or "N/A"}\n\nDETAILS:\n{data["description"]}'
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.EMAIL, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('dashboard')
    else:
        form = EmailMailboxForm()
    return render(request, 'service_desk/forms/email_issue.html', {'form': form})


@login_required
def report_hardware_issue(request):
    if request.method == 'POST':
        form = HardwareIssueForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            title = f'[Portal] Hardware Issue: {data["device_type"]} - {data["summary"]}'
            desc = f'USER REPORT:\n-----------------\nDevice: {data["device_type"]}\nModel: {data["device_model"] or "Unknown"}\nSerial: {data["serial_number"] or "N/A"}\n\nDETAILS:\n{data["description"]}'
            Ticket.objects.create(
                title=title,
                description=desc,
                ticket_type=Ticket.TicketType.HARDWARE,
                submitter=request.user,
                priority=Ticket.Priority.P3,
                status=Ticket.Status.NEW
            )
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('dashboard')
    else:
        form = HardwareIssueForm()
    return render(request, 'service_desk/forms/hardware_issue.html', {'form': form})


@login_required
def report_printer_issue(request):
    if request.method == 'POST':
        form = PrinterScannerForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            title = f'[Portal] Printer Issue at {data["printer_location"]}'
            desc = f'USER REPORT:\n-----------------\nLocation: {data["printer_location"]}\nComputer: {data["computer_name"] or "N/A"}\n\nDETAILS:\n{data["description"]}'
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.PRINTER, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('dashboard')
    else:
        form = PrinterScannerForm()
    return render(request, 'service_desk/forms/printer_issue.html', {'form': form})


@login_required
def report_software_install(request):
    if request.method == 'POST':
        form = SoftwareInstallForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            target = data['target_user'] if data['target_user'] else 'Self'
            title = f'[Portal] Software Install: {data["software_name"]} for {target}'
            desc = f'USER REPORT:\n-----------------\nSoftware: {data["software_name"]}\nFor: {target}\nComputer: {data["computer_name"]}\nLicense Info: {data["license_info"] or "N/A"}\n\nDETAILS:\n{data["justification"]}'
            Ticket.objects.create(
                title=title,
                description=desc,
                ticket_type=Ticket.TicketType.SOFTWARE,
                submitter=request.user,
                priority=Ticket.Priority.P4,
                status=Ticket.Status.NEW
            )
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('dashboard')
    else:
        form = SoftwareInstallForm()
    return render(request, 'service_desk/forms/software_install.html', {'form': form})


@login_required
def report_general_question(request):
    if request.method == 'POST':
        form = GeneralQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            title = f'[Portal] General Question: {data["summary"]}'
            Ticket.objects.create(
                title=title,
                description=data['description'],
                ticket_type=Ticket.TicketType.GENERAL,
                submitter=request.user,
                priority=Ticket.Priority.P4,
                status=Ticket.Status.NEW
            )
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('dashboard')
    else:
        form = GeneralQuestionForm()
    return render(request, 'service_desk/forms/general_question.html', {'form': form})


@login_required
def report_vp_reset(request):
    if request.method == 'POST':
        form = VPResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            target_user = data['deltek_username'] if data['deltek_username'] else data['your_name']
            title = f'[Portal] VP Password Reset: {target_user}'
            desc = f'USER REPORT:\n-----------------\nName: {data["your_name"]}\nDeltek Username: {target_user}\n\nDETAILS:\n{data["summary"]}'
            Ticket.objects.create(
                title=title,
                description=desc,
                ticket_type=Ticket.TicketType.VP_RESET,
                submitter=request.user,
                priority=Ticket.Priority.P3,
                status=Ticket.Status.NEW
            )
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('dashboard')
    else:
        form = VPResetForm()
    return render(request, 'service_desk/forms/vp_reset.html', {'form': form})


@login_required
def report_vp_permissions(request):
    if request.method == 'POST':
        form = VPPermissionsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            title = f'[Portal] VP Permissions: {data["your_name"]} - {data["requested_access"]}'
            desc = f'USER REPORT:\n-----------------\nName: {data["your_name"]}\nProject: {data["project_name"]}\nAccess Requested: {data["requested_access"]}\nManager: {data["manager_name"]}\n\nJUSTIFICATION:\n{data["justification"]}'
            Ticket.objects.create(
                title=title,
                description=desc,
                ticket_type=Ticket.TicketType.VP_PERM,
                submitter=request.user,
                priority=Ticket.Priority.P3,
                status=Ticket.Status.NEW
            )
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('dashboard')
    else:
        form = VPPermissionsForm()
    return render(request, 'service_desk/forms/vp_permissions.html', {'form': form})


# --- TICKET DETAIL VIEW ---
@login_required
def ticket_detail(request, ticket_id):
    is_demo_mode = ticket_service.USE_MOCK_DATA
    if is_demo_mode:
        ticket = ticket_service.get_ticket_by_id(ticket_id)
        if not ticket:
            messages.error(request, "Ticket not found.")
            return redirect('dashboard')
        comments = []
    else:
        ticket = get_object_or_404(Ticket, id=ticket_id)
        comments = ticket.comments.all().order_by('created_at')
        if request.method == 'POST':
            form = TicketReplyForm(request.POST)
            if form.is_valid():
                Comment.objects.create(
                    ticket=ticket,
                    author=request.user,
                    text=form.cleaned_data['comment']
                )
                messages.success(request, "Comment added successfully.")
                return redirect('ticket_detail', ticket_id=ticket_id)
        else:
            form = TicketReplyForm()
        return render(request, 'service_desk/ticket_detail.html', {
            'ticket': ticket,
            'comments': comments,
            'form': form,
            'is_demo_mode': is_demo_mode
        })
    return render(request, 'service_desk/ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'is_demo_mode': is_demo_mode
    })


# --- TICKET SURVEY ---
@login_required
def ticket_survey(request, ticket_id):
    is_demo_mode = ticket_service.USE_MOCK_DATA
    if is_demo_mode:
        ticket = ticket_service.get_ticket_by_id(ticket_id)
        if not ticket:
            messages.error(request, "Ticket not found.")
            return redirect('dashboard')
    else:
        ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        if is_demo_mode:
            messages.success(request, f"Demo Mode: Feedback received (Rating: {rating}/5). Data not saved.")
        else:
            messages.success(request, f"Thank you for your feedback! Your rating: {rating}/5")
        return redirect('dashboard')
    return render(request, 'service_desk/ticket_survey.html', {'ticket': ticket, 'is_demo_mode': is_demo_mode})


# --- MANAGEMENT HUB ---
@user_passes_test(lambda u: u.is_superuser)
def management_hub(request):
    return render(request, 'service_desk/management_hub.html')


# --- MANAGER DASHBOARD ---
@user_passes_test(lambda u: u.is_superuser)
def manager_dashboard(request):
    date_range = request.GET.get('range', '7d')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    analytics = ticket_service.get_dashboard_stats(date_range=date_range, start_date=start_date, end_date=end_date)
    return render(request, 'service_desk/manager_dashboard.html', {
        'analytics': analytics,
        'current_range': date_range
    })


# --- ADMIN SETTINGS (SYSTEM HEALTH CMS) ---
@user_passes_test(lambda u: u.is_superuser)
def admin_settings(request):
    stats = ticket_service.get_dashboard_stats()
    current_health = stats.get('system_health') or {}

    if request.method == 'POST':
        announcement_title = request.POST.get('announcement_title')
        announcement_message = request.POST.get('announcement_message')
        announcement_type = request.POST.get('announcement_type')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        vendor_status = []
        for i in range(20):
            name = request.POST.get(f'vendor_name_{i}')
            status = request.POST.get(f'vendor_status_{i}')
            if name:
                vendor_status.append({'name': name, 'status': status})

        new_health_data = {
            'announcement': {
                'title': announcement_title,
                'message': announcement_message,
                'type': announcement_type,
                'date': 'Today',
                'start_datetime': start_time,
                'end_datetime': end_time
            },
            'vendor_status': vendor_status
        }
        # Service layer handles logging; also explicit audit entry per spec
        ticket_service.update_system_health(new_health_data, user=request.user.username)
        ticket_service.log_system_event(request.user.username, 'Updated System Health', 'System Health', 'Admin Settings saved')
        messages.success(request, "System Health settings updated successfully!")
        return redirect('admin_settings')

    return render(request, 'service_desk/admin_settings.html', {'current_health': current_health})


# --- TECHNICIAN PROFILE ---
@user_passes_test(lambda u: u.is_superuser)
def technician_profile(request, name):
    tech = ticket_service.get_technician_details(name)
    if not tech:
        messages.error(request, "Technician not found.")
        return redirect('manager_dashboard')
    return render(request, 'service_desk/technician_profile.html', {'technician': tech})


# --- CSAT REPORT ---
@user_passes_test(lambda u: u.is_superuser)
def csat_report(request, tech_id=None):
    date_range = request.GET.get('range', '7d')
    technician = None
    feedback_data = []

    if tech_id:
        technician = ticket_service.get_technician_details(tech_id)
        if technician:
            source_feedback = technician.get('feedback', [])
        else:
            source_feedback = []
    else:
        stats = ticket_service.get_dashboard_stats(date_range)
        source_feedback = stats.get('recent_feedback', [])

    if date_range == 'today':
        feedback_data = source_feedback[:1]
    elif date_range == 'yesterday':
        feedback_data = source_feedback[:2]
    elif date_range == '30d':
        feedback_data = source_feedback
    else:  # 7d default
        feedback_data = source_feedback[:3]

    return render(request, 'service_desk/csat_report.html', {
        'current_range': date_range,
        'technician': technician,
        'feedback': feedback_data
    })


# --- KNOWLEDGE BASE VIEWER ---
@login_required
def kb_home(request):
    search_query = request.GET.get('q')
    category_filter = request.GET.get('category')
    articles = ticket_service.get_knowledge_base_articles(search_query=search_query)
    if category_filter:
        articles = [a for a in articles if a.get('category') == category_filter]
    recent_articles = sorted(articles, key=lambda x: x.get('updated_at', ''), reverse=True)[:10]
    return render(request, 'knowledge_base/kb_home.html', {
        'articles': articles,
        'recent_articles': recent_articles,
        'search_query': search_query,
        'current_category': category_filter
    })


@login_required
def article_detail(request, article_id):
    articles = ticket_service.get_knowledge_base_articles()
    article = next((a for a in articles if a['id'] == article_id), None)
    if not article:
        messages.error(request, "Article not found.")
        return redirect('kb_home')
    return render(request, 'knowledge_base/article_detail.html', {'article': article})


# --- KB MANAGER (ADMIN TABLE) ---
@user_passes_test(lambda u: u.is_superuser)
def kb_manager(request):
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    sort_by = request.GET.get('sort', '-id')

    all_articles = ticket_service.get_knowledge_base_articles()
    total_count = len(all_articles)
    draft_count = sum(1 for a in all_articles if a.get('status') == 'Draft')
    pending_count = sum(1 for a in all_articles if a.get('status') == 'Pending Approval')

    filtered_articles = all_articles
    if search_query:
        q = search_query.lower()
        filtered_articles = [
            a for a in filtered_articles
            if q in a.get('title', '').lower()
            or q in a.get('problem', '').lower()
            or q in a.get('solution', '').lower()
            or q in a.get('category', '').lower()
            or q in a.get('subcategory', '').lower()
        ]

    if category_filter and category_filter != 'All':
        filtered_articles = [a for a in filtered_articles if a.get('category') == category_filter]

    reverse = False
    sort_field = sort_by
    if sort_by.startswith('-'):
        reverse = True
        sort_field = sort_by[1:]

    def sort_key(article):
        val = article.get(sort_field, '')
        if sort_field == 'id':
            try:
                return int(val)
            except Exception:
                return 0
        return str(val).lower()

    filtered_articles = sorted(filtered_articles, key=sort_key, reverse=reverse)

    return render(request, 'knowledge_base/kb_manager.html', {
        'articles': filtered_articles,
        'total_count': total_count,
        'draft_count': draft_count,
        'pending_count': pending_count,
        'search_query': search_query,
        'current_category': category_filter,
        'current_sort': sort_by
    })


# --- KB ADD ---
@user_passes_test(lambda u: u.is_superuser)
def kb_add(request):
    if request.method == 'POST':
        form = KBArticleForm(request.POST)
        if form.is_valid():
            ticket_service.create_kb_article(form.cleaned_data, user=request.user.username)
            messages.success(request, "Article created successfully!")
            return redirect('kb_manager')
    else:
        form = KBArticleForm()
    return render(request, 'knowledge_base/kb_add.html', {'form': form})


# --- KB EDIT ---
@user_passes_test(lambda u: u.is_superuser)
def kb_edit(request, article_id):
    articles = ticket_service.get_knowledge_base_articles()
    article = next((a for a in articles if a['id'] == article_id), None)
    if not article:
        return redirect('kb_home')

    if request.method == 'POST':
        form = KBArticleForm(request.POST)
        if form.is_valid():
            ticket_service.update_kb_article(article_id, form.cleaned_data, user=request.user.username)
            messages.success(request, "Article updated successfully.")
            return redirect('article_detail', article_id=article_id)
    else:
        initial_data = {
            'title': article.get('title', ''),
            'category': article.get('category', ''),
            'subcategory': article.get('subcategory', ''),
            'status': article.get('status', 'Approved'),
            'problem': article.get('problem', ''),
            'solution': article.get('solution', ''),
            'internal_notes': article.get('internal_notes', '')
        }
        form = KBArticleForm(initial=initial_data)
    return render(request, 'knowledge_base/kb_edit.html', {'form': form, 'article': article})


# --- KB DELETE ---
@user_passes_test(lambda u: u.is_superuser)
def kb_delete(request, article_id):
    if request.method == 'POST':
        result = ticket_service.delete_kb_article(article_id, user=request.user.username)
        if result:
            messages.success(request, "Article deleted successfully.")
        else:
            messages.error(request, "Article not found.")
    return redirect('kb_manager')


# --- KB BULK ACTIONS ---
@user_passes_test(lambda u: u.is_superuser)
def kb_bulk_action(request):
    if request.method != 'POST':
        return redirect('kb_manager')

    selected_ids = request.POST.getlist('selected_ids')
    action = request.POST.get('bulk_action')

    if not selected_ids:
        messages.error(request, "No articles selected.")
        return redirect('kb_manager')
    if not action:
        messages.error(request, "No action specified.")
        return redirect('kb_manager')

    try:
        result = ticket_service.bulk_update_kb_articles(selected_ids, action, user=request.user.username)
        if result:
            action_map = {
                'approve': 'Approved',
                'draft': 'Draft',
                'pending': 'Pending Approval',
                'delete': 'Deleted'
            }
            status_text = action_map.get(action, 'Updated')
            messages.success(request, f"Bulk action completed: {len(selected_ids)} article(s) {status_text}.")
        else:
            messages.error(request, "Bulk action failed.")
    except Exception as e:
        messages.error(request, f"Error during bulk action: {e}")
    return redirect('kb_manager')


# --- SYSTEM LOGS VIEW ---
@user_passes_test(lambda u: u.is_superuser)
def system_logs(request):
    """
    System Activity Log Viewer.
    Handles: Timezone Conversion, Search, and Sorting.
    """
    # 1. Setup Timezones (ID, Friendly Label)
    NA_TIMEZONES = [
        ('America/New_York', 'Eastern Time (ET)'),
        ('America/Chicago', 'Central Time (CT)'),
        ('America/Denver', 'Mountain Time (MT)'),
        ('America/Los_Angeles', 'Pacific Time (PT)'),
        ('America/Anchorage', 'Alaska Time (AKT)'),
        ('Pacific/Honolulu', 'Hawaii Time (HST)')  # Fixed: Changed from America/Honolulu
    ]
    selected_tz_name = request.GET.get('timezone', 'America/New_York')
    
    # 2. Activate the selected timezone for this request
    timezone.activate(selected_tz_name)
    
    # 3. Get Params
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-timestamp')

    # 4. Fetch Logs
    logs = ticket_service.get_system_logs()

    # 5. Process & Convert Dates (Simplified with timezone.activate)
    processed_logs = []
    utc = pytz.UTC
    
    for log in logs:
        try:
            # Parse the ISO timestamp string
            dt_utc = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
            
            # Ensure it's timezone-aware (in UTC)
            if dt_utc.tzinfo is None:
                dt_utc = timezone.make_aware(dt_utc, utc)
            
            # Store the aware datetime (template will auto-convert to active timezone)
            log['dt_obj'] = dt_utc
        except (ValueError, TypeError):
            log['dt_obj'] = datetime.min.replace(tzinfo=utc)
        processed_logs.append(log)

    # 6. Apply Search
    if search_query:
        q = search_query.lower()
        processed_logs = [
            l for l in processed_logs
            if q in l.get('user', '').lower()
            or q in l.get('action', '').lower()
            or q in l.get('target', '').lower()
            or q in l.get('details', '').lower()
        ]

    # 7. Apply Sorting
    reverse = False
    sort_field = sort_by
    if sort_by.startswith('-'):
        reverse = True
        sort_field = sort_by[1:]

    def sort_key(item):
        if sort_field == 'timestamp':
            return item['dt_obj']
        return str(item.get(sort_field, '')).lower()

    processed_logs = sorted(processed_logs, key=sort_key, reverse=reverse)

    return render(request, 'service_desk/system_logs.html', {
        'logs': processed_logs,
        'search_query': search_query,
        'current_sort': sort_by,
        'na_timezones': NA_TIMEZONES,
        'selected_tz': selected_tz_name
    })
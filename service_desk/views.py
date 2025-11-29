from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .forms import (
    ApplicationIssueForm, EmailMailboxForm, HardwareIssueForm, PrinterScannerForm,
    SoftwareInstallForm, GeneralQuestionForm, VPResetForm, VPPermissionsForm,
    TicketReplyForm, KBArticleForm
)
from .models import Ticket, Comment
from services import ticket_service

# --- USER DASHBOARD ---
@login_required
def dashboard(request):
    """
    Main Dashboard: Shows user's tickets with sorting capability.
    Now supports Integer sorting for IDs.
    """
    sort_by = request.GET.get('sort', '-created_at')
    
    # Fetch tickets
    tickets = ticket_service.get_all_tickets(user=request.user)
    
    # Sort logic
    if sort_by.startswith('-'):
        reverse = True
        sort_field = sort_by[1:]
    else:
        reverse = False
        sort_field = sort_by
    
    if sort_field in ['id', 'title', 'ticket_type', 'status', 'priority', 'created_at']:
        def sort_key(t):
            val = t.get(sort_field, '')
            # Integer Sort for ID
            if sort_field == 'id':
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return 0
            # String Sort for others
            return str(val).lower()

        tickets = sorted(tickets, key=sort_key, reverse=reverse)
    
    stats = ticket_service.get_ticket_stats(tickets)
    dashboard_stats = ticket_service.get_dashboard_stats()
    
    return render(request, 'service_desk/dashboard.html', {
        'tickets': tickets,
        'stats': stats,
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
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.APPLICATION, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
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
            title = f'[Portal] Email: {data["issue_type"]}'
            desc = f'USER REPORT:\n-----------------\nIssue Type: {data["issue_type"]}\nEmail: {data["email_address"]}\n\nDETAILS:\n{data["description"]}'
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.EMAIL, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('dashboard')
    else:
        form = EmailMailboxForm()
    return render(request, 'service_desk/forms/email_mailbox.html', {'form': form})

@login_required
def report_hardware_issue(request):
    if request.method == 'POST':
        form = HardwareIssueForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            title = f'[Portal] Hardware: {data["hardware_type"]} - {data["summary"]}'
            desc = f'USER REPORT:\n-----------------\nHardware: {data["hardware_type"]}\nAsset: {data["asset_tag"] or "Unknown"}\nLocation: {data["location"] or "N/A"}\n\nDETAILS:\n{data["description"]}'
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.HARDWARE, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
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
            title = f'[Portal] Printer: {data["printer_location"]}'
            desc = f'USER REPORT:\n-----------------\nLocation: {data["printer_location"]}\nComputer: {data["computer_name"] or "Primary"}\n\nDETAILS:\n{data["description"]}'
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
            user_display = 'Myself'
            if data['request_for'] == 'Another User':
                user_display = f'Another User ({data["target_user"]})'
            title = f'[Portal] Software Request: {data["software_name"]}'
            desc = f'USER REPORT:\n-----------------\nSoftware: {data["software_name"]}\nRequest For: {user_display}\nComputer: {data["computer_name"]}\n\nJUSTIFICATION:\n{data["justification"]}\n\nLICENSE:\n{data["license_info"] or "None"}'
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.SOFTWARE, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
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
            Ticket.objects.create(title=title, description=data['description'], ticket_type=Ticket.TicketType.GENERAL, submitter=request.user, priority=Ticket.Priority.P4, status=Ticket.Status.NEW)
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
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.VP_RESET, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
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
            req_type = data['request_type']
            if req_type == 'Other' and data['other_type']:
                req_type = f'Other ({data["other_type"]})'
            title = f'[Portal] VP Permissions: {req_type}'
            desc = f'USER REPORT:\n-----------------\nRequest Type: {req_type}\nProject: {data["affected_project"] or "N/A"}\nUsers: {data["user_list"] or "N/A"}\n\nDETAILS:\n{data["summary"]}'
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.VP_PERM, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
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
        form = TicketReplyForm()
        if request.method == 'POST':
            form = TicketReplyForm(request.POST)
            if form.is_valid():
                messages.warning(request, "Demo Mode: Your changes were not saved to the database.")
                return redirect('ticket_detail', ticket_id=ticket_id)
    else:
        ticket = get_object_or_404(Ticket, id=ticket_id)
        comments = ticket.comments.all()
        if request.method == 'POST':
            form = TicketReplyForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if data['comment']:
                    Comment.objects.create(ticket=ticket, author=request.user, text=data['comment'])
                    messages.success(request, "Your comment has been added.")
                if data['priority']:
                    ticket.priority = data['priority']
                    ticket.save()
                    messages.success(request, f"Priority updated to {ticket.get_priority_display()}.")
                if data['close_ticket']:
                    ticket.status = Ticket.Status.CLOSED
                    ticket.save()
                    messages.success(request, "Ticket has been closed.")
                return redirect('ticket_detail', ticket_id=ticket.id)
        else:
            form = TicketReplyForm(initial={'priority': ticket.priority})
    
    return render(request, 'service_desk/ticket_detail.html', {'ticket': ticket, 'comments': comments, 'form': form, 'is_demo_mode': is_demo_mode})

# --- TICKET SURVEY ---
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

# --- MANAGER TOOLS ---

@user_passes_test(lambda u: u.is_superuser)
def management_hub(request):
    """ Admin Launchpad """
    return render(request, 'service_desk/management_hub.html')

@user_passes_test(lambda u: u.is_superuser)
def manager_dashboard(request):
    date_range = request.GET.get('range', '7d')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    analytics = ticket_service.get_dashboard_stats(date_range=date_range, start_date=start_date, end_date=end_date)
    return render(request, 'service_desk/manager_dashboard.html', {'analytics': analytics, 'current_range': date_range})

@user_passes_test(lambda u: u.is_superuser)
def admin_settings(request):
    current_health = ticket_service.get_dashboard_stats()['system_health']
    if request.method == 'POST':
        announcement_title = request.POST.get('announcement_title')
        announcement_message = request.POST.get('announcement_message')
        announcement_type = request.POST.get('announcement_type')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        vendor_status = []
        vendor_names = request.POST.getlist('vendor_name[]')
        vendor_statuses = request.POST.getlist('vendor_status[]')
        for name, status in zip(vendor_names, vendor_statuses):
            if name:
                vendor_status.append({'name': name, 'status': status})
        
        new_health_data = {
            'announcement': {
                'title': announcement_title,
                'message': announcement_message,
                'type': announcement_type,
                'start_time': start_time,
                'end_time': end_time,
                'date': 'Today'
            },
            'vendor_status': vendor_status
        }
        ticket_service.update_system_health(new_health_data)
        messages.success(request, "System Health settings updated successfully!")
        return redirect('admin_settings')
    return render(request, 'service_desk/admin_settings.html', {'current_health': current_health})

@user_passes_test(lambda u: u.is_superuser)
def technician_profile(request, name):
    tech_data = ticket_service.get_technician_details(name)
    if not tech_data:
        messages.error(request, f"Technician profile not found: {name}")
        return redirect('manager_dashboard')
    return render(request, 'service_desk/technician_profile.html', {'technician': tech_data})

@user_passes_test(lambda u: u.is_superuser)
def csat_report(request, tech_id=None):
    """
    CSAT Report: Displays feedback. Can be Global or Filtered by Technician.
    """
    # 1. Get Date Range from URL (Default to '7d')
    date_range = request.GET.get('range', '7d')
    
    # 2. Setup Variables
    technician = None
    feedback_data = []
    
    # 3. Fetch Data based on Filter
    if tech_id:
        # Technician Specific Report
        technician = ticket_service.get_technician_details(tech_id)
        if technician:
            # Get the specific feedback list from the roster
            feedback_data = technician.get('feedback', [])
    else:
        # Global Report
        # Re-use dashboard stats to pull the global 'recent_feedback' list
        stats = ticket_service.get_dashboard_stats(date_range)
        feedback_data = stats.get('recent_feedback', [])

    # 4. Render Template
    return render(request, 'service_desk/csat_report.html', {
        'current_range': date_range,
        'technician': technician,
        'feedback_data': feedback_data
    })

# --- KNOWLEDGE BASE (VIEWER & EDITOR) ---

@login_required
def kb_home(request):
    """ KB Viewer """
    search_query = request.GET.get('q')
    category_filter = request.GET.get('category')
    
    articles = ticket_service.get_knowledge_base_articles(search_query)
    
    if category_filter:
        articles = [a for a in articles if a.get('category') == category_filter]
        
    recent_articles = articles[:10]
    return render(request, 'knowledge_base/kb_home.html', {
        'articles': articles,
        'recent_articles': recent_articles,
        'search_query': search_query,
        'current_category': category_filter
    })

@login_required
def article_detail(request, article_id):
    """ KB Article Reader """
    articles = ticket_service.get_knowledge_base_articles()
    article = next((a for a in articles if a['id'] == article_id), None)
    if not article:
        messages.error(request, "Article not found.")
        return redirect('kb_home')
    return render(request, 'knowledge_base/article_detail.html', {'article': article})

@user_passes_test(lambda u: u.is_superuser)
def kb_manager(request):
    """ 
    KB Admin Table.
    Handles: Search, Category Filtering, Sorting, and Status Counts.
    """
    # 1. Get Query Parameters
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    sort_by = request.GET.get('sort', '-id')
    
    # 2. Fetch ALL articles
    all_articles = ticket_service.get_knowledge_base_articles()
    
    # 3. Calculate Stats (Before filtering)
    total_count = len(all_articles)
    draft_count = sum(1 for a in all_articles if a.get('status') == 'Draft')
    pending_count = sum(1 for a in all_articles if a.get('status') == 'Pending Approval')
    
    # 4. Apply Search Filter
    filtered_articles = all_articles
    if search_query:
        q = search_query.lower()
        filtered_articles = [
            a for a in filtered_articles 
            if q in a.get('title', '').lower() 
            or q in a.get('category', '').lower()
            or q in a.get('subcategory', '').lower()
        ]
        
    # 5. Apply Category Filter
    if category_filter and category_filter != 'All':
        filtered_articles = [
            a for a in filtered_articles 
            if a.get('category') == category_filter
        ]

    # 6. Apply Sorting
    reverse = False
    sort_field = sort_by
    if sort_by.startswith('-'):
        reverse = True
        sort_field = sort_by[1:]
        
    def sort_key(article):
        val = article.get(sort_field, '')
        if sort_field == 'id':
            try: return int(val)
            except: return 0
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

@user_passes_test(lambda u: u.is_superuser)
def kb_add(request):
    """ KB Create Article """
    if request.method == 'POST':
        form = KBArticleForm(request.POST)
        if form.is_valid():
            ticket_service.create_kb_article(form.cleaned_data)
            messages.success(request, "Article created successfully.")
            return redirect('kb_home')
    else:
        form = KBArticleForm()
    return render(request, 'knowledge_base/kb_form.html', {'form': form, 'title': 'Add Article'})

@user_passes_test(lambda u: u.is_superuser)
def kb_edit(request, article_id):
    """ KB Edit Article """
    articles = ticket_service.get_knowledge_base_articles()
    article = next((a for a in articles if a['id'] == article_id), None)
    if not article:
        return redirect('kb_home')
        
    if request.method == 'POST':
        form = KBArticleForm(request.POST)
        if form.is_valid():
            ticket_service.update_kb_article(article_id, form.cleaned_data)
            messages.success(request, "Article updated successfully.")
            return redirect('article_detail', article_id=article_id)
    else:
        # Pre-fill form
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
        
    return render(request, 'knowledge_base/kb_form.html', {'form': form, 'article_id': article_id, 'title': 'Edit Article'})

@user_passes_test(lambda u: u.is_superuser)
def kb_delete(request, article_id):
    """ KB Delete Article """
    ticket_service.delete_kb_article(article_id)
    messages.success(request, "Article deleted.")
    return redirect('kb_home')
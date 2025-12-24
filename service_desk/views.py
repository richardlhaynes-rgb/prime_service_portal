from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import (
    ApplicationIssueForm, EmailMailboxForm, HardwareIssueForm, PrinterScannerForm,
    SoftwareInstallForm, GeneralQuestionForm, VPResetForm, VPPermissionsForm,
    TicketReplyForm, KBArticleForm, GlobalSettingsForm, CustomUserCreationForm, CustomUserChangeForm
)
from .models import Ticket, Comment, GlobalSettings
from services import ticket_service
from datetime import datetime, timedelta
import random
from django.contrib.auth.models import User, Group
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from knowledge_base.models import KBCategory, KBSubcategory, Article
from django.db import transaction
import pytz
from django.utils.dateparse import parse_datetime

# ============================================================================
# USER DASHBOARD
# ============================================================================

@login_required
def dashboard(request):
    """
    User Dashboard - Shows the logged-in user's tickets and stats.
    Uses real database data from the Ticket model.
    """
    # Fetch all tickets for the current user
    user_tickets = Ticket.objects.filter(submitter=request.user).order_by('-created_at')
    
    # Calculate ticket stats
    open_statuses = ['New', 'User Commented', 'Work In Progress', 'Reopened', 'Assigned', 'In Progress', 'Awaiting User Reply', 'On Hold']
    resolved_statuses = ['Resolved', 'Cancelled']
    
    open_tickets = user_tickets.filter(status__in=open_statuses).count()
    resolved_tickets = user_tickets.filter(status__in=resolved_statuses).count()
    total_tickets = user_tickets.count()
    
    # Find a resolved ticket that needs feedback (no CSAT survey submitted)
    feedback_ticket = Ticket.objects.filter(
        submitter=request.user,
        status='Resolved'
    ).filter(
        survey__isnull=True  # No CSATSurvey linked
    ).order_by('-updated_at').first()
    
    # Handle sorting
    sort_param = request.GET.get('sort', '-created_at')
    valid_sort_fields = ['id', '-id', 'title', '-title', 'ticket_type', '-ticket_type', 
                         'priority', '-priority', 'status', '-status', 'created_at', '-created_at']
    if sort_param in valid_sort_fields:
        user_tickets = user_tickets.order_by(sort_param)
    
    context = {
        'tickets': user_tickets,
        'open_tickets': open_tickets,
        'resolved_tickets': resolved_tickets,
        'total_tickets': total_tickets,
        'feedback_ticket': feedback_ticket,
        'current_sort': sort_param,
    }
    
    return render(request, 'service_desk/dashboard.html', context)


# ============================================================================
# SERVICE CATALOG
# ============================================================================

@login_required
def service_catalog(request):
    settings = GlobalSettings.load()

    articles = ticket_service.get_knowledge_base_articles()
    recommended_articles = []

    if articles:
        strategy = settings.kb_recommendation_logic
        if strategy == 'random':
            recommended_articles = random.sample(articles, k=min(3, len(articles)))
        elif strategy == 'views':
            recommended_articles = sorted(articles, key=lambda a: a.get('views', 0), reverse=True)[:3]
        else:  # 'updated' or fallback
            recommended_articles = sorted(articles, key=lambda a: a.get('updated_at', ''), reverse=True)[:3]

    return render(request, 'service_desk/service_catalog.html', {
        'recommended_articles': recommended_articles
    })


# ============================================================================
# TICKET SUBMISSION FORMS (8 Service Cards)
# ============================================================================

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
            title = f'[Portal] Email Issue: {data["email_address"]} - {data["summary"]}'
            desc = f'USER REPORT:\n-----------------\nEmail: {data["email_address"]}\n\nDETAILS:\n{data["description"]}'
            Ticket.objects.create(
                title=title,
                description=desc,
                ticket_type=Ticket.TicketType.EMAIL,
                submitter=request.user,
                priority=Ticket.Priority.P3,
                status=Ticket.Status.NEW
            )
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('dashboard')
    else:
        form = EmailMailboxForm()
    return render(request, 'service_desk/forms/email_issue.html', {'form': form})


@login_required
def report_hardware_issue(request):
    if request.method == 'POST':
        form = HardwareIssueForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            device = data['device_type']
            if device == 'Other' and data['other_device']:
                device = f'Other ({data["other_device"]})'
            title = f'[Portal] Hardware Issue: {device} - {data["summary"]}'
            desc = f'USER REPORT:\n-----------------\nDevice: {device}\nSerial/Tag: {data.get("device_serial", "N/A")}\n\nDETAILS:\n{data["description"]}'
            Ticket.objects.create(
                title=title,
                description=desc,
                ticket_type=Ticket.TicketType.HARDWARE,
                submitter=request.user,
                priority=Ticket.Priority.P2 if data.get('is_urgent') else Ticket.Priority.P3,
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
            device = data['device_type']
            title = f'[Portal] Printer/Scanner Issue: {device} - {data["summary"]}'
            desc = f'USER REPORT:\n-----------------\nDevice: {device}\nLocation: {data.get("location", "N/A")}\n\nDETAILS:\n{data["description"]}'
            Ticket.objects.create(
                title=title,
                description=desc,
                ticket_type=Ticket.TicketType.PRINTER,
                submitter=request.user,
                priority=Ticket.Priority.P3,
                status=Ticket.Status.NEW
            )
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
            app = data['software_name']
            title = f'[Portal] Software Request: {app}'
            desc = f'USER REPORT:\n-----------------\nSoftware: {app}\n\nJUSTIFICATION:\n{data["justification"]}'
            Ticket.objects.create(
                title=title,
                description=desc,
                ticket_type=Ticket.TicketType.SOFTWARE,
                submitter=request.user,
                priority=Ticket.Priority.P3,
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


# ============================================================================
# TICKET DETAIL & SURVEY
# ============================================================================

@login_required
def ticket_detail(request, ticket_id):
    """
    Ticket Detail View - Shows full ticket information and activity log.
    Handles comments, priority updates, and ticket closure.
    Uses real database data exclusively.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    comments = ticket.comments.all().order_by('created_at')
    
    if request.method == 'POST':
        form = TicketReplyForm(request.POST)
        changes_made = False
        action_summary = []
        
        if form.is_valid():
            # 1. Handle Comment
            comment_text = form.cleaned_data.get('comment', '').strip()
            if comment_text:
                Comment.objects.create(
                    ticket=ticket,
                    author=request.user,
                    text=comment_text,
                    is_internal=False
                )
                action_summary.append('comment added')
                changes_made = True
                
                if ticket.status == 'Awaiting User Reply':
                    ticket.status = 'User Commented'
            
            # 2. Handle Priority Update
            new_priority = request.POST.get('priority')
            if new_priority and new_priority != ticket.priority:
                old_priority = ticket.priority
                ticket.priority = new_priority
                action_summary.append(f'priority changed from "{old_priority}" to "{new_priority}"')
                changes_made = True
            
            # 3. Handle Ticket Closure
            close_ticket = request.POST.get('close_ticket')
            if close_ticket == 'on':
                ticket.status = 'Resolved'
                ticket.closed_at = timezone.now() # IMPORTANT: Set closed timestamp
                action_summary.append('ticket marked as Resolved')
                changes_made = True
                
                if not ticket.technician:
                    ticket.technician = request.user
                    action_summary.append(f'assigned to {request.user.get_full_name() or request.user.username}')
                
                Comment.objects.create(
                    ticket=ticket,
                    author=request.user,
                    text=f"Ticket closed by {request.user.get_full_name() or request.user.username}.",
                    is_internal=True
                )
            
            if changes_made:
                ticket.save()
                message = f"Ticket updated: {', '.join(action_summary)}."
                # Only show flash message for standard requests
                if not request.headers.get('HX-Request'):
                    messages.success(request, message)
            else:
                if not request.headers.get('HX-Request'):
                    messages.info(request, "No changes were made to the ticket.")
            
            # HTMX Response: Return only the updated activity log partial
            if request.headers.get('HX-Request'):
                updated_comments = ticket.comments.all().order_by('created_at')
                return render(request, 'service_desk/partials/ticket_activities.html', {
                    'comments': updated_comments, 
                    'request': request
                })

            return redirect('ticket_detail', ticket_id=ticket_id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TicketReplyForm(initial={'priority': ticket.priority})
    
    can_reopen = ticket.status in ['Resolved', 'Cancelled']
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'form': form,
        'can_reopen': can_reopen,
        'is_demo_mode': False,
    }
    
    return render(request, 'service_desk/ticket_detail.html', context)


@login_required
def ticket_survey(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    existing_survey = getattr(ticket, 'survey', None)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except (TypeError, ValueError):
            messages.error(request, 'Please select a valid rating (1-5 stars).')
            return redirect('ticket_survey', ticket_id=ticket_id)
        
        # Use update_or_create from the specific related model or just create
        from .models import CSATSurvey
        CSATSurvey.objects.update_or_create(
            ticket=ticket,
            defaults={
                'rating': rating,
                'comment': comment,
                'submitted_by': request.user,
            }
        )
        
        messages.success(request, 'Thank you for your feedback! Your response has been recorded.')
        return redirect('dashboard')
    
    context = {
        'ticket': {
            'id': ticket.id,
            'title': ticket.title,
            'technician_name': ticket.technician.get_full_name() if ticket.technician else 'Support Team',
        },
        'existing_survey': existing_survey,
    }
    
    return render(request, 'service_desk/ticket_survey.html', context)


# ============================================================================
# MANAGEMENT HUB & MANAGER TOOLS
# ============================================================================

@user_passes_test(lambda u: u.is_superuser)
def management_hub(request):
    return render(request, 'service_desk/management_hub.html')


@user_passes_test(lambda u: u.is_superuser)
def manager_dashboard(request):
    """
    Manager Analytics Dashboard.
    - Preserves existing buttons (Today, Yesterday, 7d, 30d)
    - Adds logic for 'Custom Range' inputs
    - Trend Chart dynamically adapts x-axis based on selected duration
    """
    from django.db.models import Count, Avg, F
    from django.contrib.auth.models import Group
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # --- 1. Date Range Handling (Presets + Custom) ---
    date_range = request.GET.get('range', '7d')
    now = timezone.now()
    
    # Defaults
    start_date = now - timedelta(days=7)
    end_date = now 

    if date_range == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'yesterday':
        yesterday = now - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif date_range == '7d':
        start_date = now - timedelta(days=7)
        end_date = now
    elif date_range == '30d':
        start_date = now - timedelta(days=30)
        end_date = now
    elif date_range == 'custom':
        try:
            start_str = request.GET.get('start', '')
            end_str = request.GET.get('end', '')
            if start_str and end_str:
                start_date = datetime.strptime(start_str, '%Y-%m-%d').replace(tzinfo=timezone.get_current_timezone())
                end_date = datetime.strptime(end_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.get_current_timezone())
        except ValueError:
            pass

    # --- 2. Query Tickets in Range ---
    tickets = Ticket.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
    total_tickets = tickets.count()

    # --- 3. Metrics Calculation ---
    resolved = tickets.filter(status__in=['Resolved', 'Closed'], closed_at__isnull=False)
    
    if resolved.exists():
        avg = resolved.aggregate(t=Avg(F('closed_at') - F('created_at')))['t']
        avg_resolution_time = f"{avg.total_seconds()/3600:.1f} hours" if avg else "0 hours"
    else:
        avg_resolution_time = "0 hours"
        
    # First Response
    responded = tickets.filter(first_response_at__isnull=False)
    if responded.exists():
        avg = responded.aggregate(t=Avg(F('first_response_at') - F('created_at')))['t']
        first_response_time = f"{int(avg.total_seconds()/60)} mins" if avg else "N/A"
    else:
        first_response_time = "N/A"
        
    priority_escalations = tickets.filter(priority__icontains='Critical').exclude(status__in=['Resolved', 'Closed']).count()
    
    # SLA Breaches
    sla_breaches_qs = tickets.filter(priority__icontains='Critical').exclude(status__in=['Resolved', 'Closed'])
    sla_breaches = []
    for t in sla_breaches_qs[:5]:
        age = (now - t.created_at).total_seconds() / 3600
        sla_breaches.append({
            'ticket_id': t.id,
            'title': t.title,
            'age_hours': round(age, 1),
            'technician': t.technician.get_full_name() if t.technician else 'Unassigned'
        })

    # --- 4. Trend Data (Dynamic Labels) ---
    days_in_range = (end_date - start_date).days + 1
    trend_labels = []
    trend_data = []
    
    for i in range(days_in_range):
        current_day_start = start_date + timedelta(days=i)
        current_day_end = current_day_start + timedelta(days=1)
        
        # Stop if we hit the future
        if current_day_start > now:
            break
            
        # Smart Labeling
        if days_in_range <= 2:
            label = current_day_start.strftime('%b %d')  # Today/Yesterday
        elif days_in_range <= 10:
            label = current_day_start.strftime('%a')  # Mon, Tue
        else:
            label = current_day_start.strftime('%b %d')  # Oct 24
            
        trend_labels.append(label)
        
        # Count tickets for this specific slice
        count = Ticket.objects.filter(created_at__gte=current_day_start, created_at__lt=current_day_end).count()
        trend_data.append(count)

    # --- 5. Roster & Charts ---
    roster = []
    res_labels = []
    res_data = []
    
    service_desk = Group.objects.filter(name='Service Desk').first()
    if service_desk:
        for member in service_desk.user_set.all():
            open_count = Ticket.objects.filter(technician=member).exclude(status__in=['Resolved', 'Closed']).count()
            
            # Avatar Logic: Respect prefer_initials setting
            if hasattr(member, 'profile') and member.profile.prefer_initials:
                # User prefers initials - always use UI Avatars
                avatar = f"https://ui-avatars.com/api/?name={member.first_name}+{member.last_name}&background=random&color=fff"
            elif hasattr(member, 'profile') and member.profile.avatar:
                # User has an uploaded avatar and doesn't prefer initials
                avatar = member.profile.avatar.url
            else:
                # Fallback to UI Avatars (initials)
                avatar = f"https://ui-avatars.com/api/?name={member.first_name}+{member.last_name}&background=random&color=fff"
            
            roster.append({
                'name': member.get_full_name(),
                'role': 'Service Desk',
                'avatar': avatar,
                'stats': {'open_tickets': open_count},
                'id': member.id
            })
            
            tech_resolved = tickets.filter(technician=member, status__in=['Resolved', 'Closed'], closed_at__isnull=False)
            if tech_resolved.exists():
                avg = tech_resolved.aggregate(a=Avg(F('closed_at') - F('created_at')))['a']
                res_labels.append(member.first_name)
                res_data.append(round(avg.total_seconds()/3600, 1))

    # Auto-Heal Bot
    roster.append({
        'name': 'Auto-Heal System',
        'role': 'Automation Bot',
        'avatar': 'https://ui-avatars.com/api/?name=AH&background=1F2937&color=fff',
        'stats': {'open_tickets': 0},
        'id': 'bot'
    })

    # Simple Charts
    status_counts = tickets.values('status').annotate(c=Count('id'))
    vol_data = {'Open': 0, 'In Progress': 0, 'Resolved': 0, 'Closed': 0}
    for i in status_counts:
        s = i['status']
        if s in ['New', 'Reopened']:
            vol_data['Open'] += i['c']
        elif s == 'Resolved':
            vol_data['Resolved'] += i['c']
        elif s in ['Closed', 'Cancelled']:
            vol_data['Closed'] += i['c']
        else:
            vol_data['In Progress'] += i['c']

    type_counts = tickets.values('ticket_type').annotate(c=Count('id')).order_by('-c')[:5]

    analytics = {
        'total_tickets': total_tickets,
        'avg_resolution_time': avg_resolution_time,
        'first_response_time': first_response_time,
        'priority_escalations': priority_escalations,
        'sla_breaches': sla_breaches,
        'volume_by_status': {'labels': list(vol_data.keys()), 'data': list(vol_data.values())},
        'tickets_by_type': {'labels': [x['ticket_type'] for x in type_counts], 'data': [x['c'] for x in type_counts]},
        'trend_data': {'labels': trend_labels, 'data': trend_data},
        'avg_resolution_time_by_member': {'labels': res_labels, 'data': res_data},
        'roster': roster
    }

    return render(request, 'service_desk/manager_dashboard.html', {
        'analytics': analytics,
        'current_range': date_range
    })


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
        ticket_service.update_system_health(new_health_data, user=request.user.username)
        messages.success(request, '✅ System health data updated.')
        return redirect('admin_settings')

    return render(request, 'service_desk/admin_settings.html', {
        'current_health': current_health
    })


@user_passes_test(lambda u: u.is_superuser)
def technician_profile(request, name):
    """
    Displays a detailed profile for a specific technician.
    Calculates real-time stats (Open, Resolved, CSAT) for the user.
    """
    from django.db.models import Count, Avg, F
    
    # 1. Handle the "Auto-Heal Bot" Edge Case
    if name == 'auto_heal_system' or name == 'bot':
        bot_context = {
            'id': 'auto_heal_system',
            'name': 'Auto-Heal System',
            'role': 'Automation Bot',
            'title': 'Automation Bot',
            'company': 'PRIME AE Group, Inc.',
            'manager_name': 'System',
            'location': 'Data Center',
            'email': 'automation@primeeng.com',
            'phone': 'N/A',
            'avatar': 'https://ui-avatars.com/api/?name=Auto+Heal&background=1F2937&color=fff',
            'stats': {
                'open_tickets': 0,
                'resolved_this_month': Ticket.objects.filter(technician__isnull=True, status='Resolved').count(),
                'avg_response': 'Instant',
                'csat_score': 'N/A'
            },
            'recent_activity': ['Automated Password Reset', 'Self-Healing Script', 'Auto-Provisioning'],
            'feedback': []
        }
        return render(request, 'service_desk/technician_profile.html', {'technician': bot_context})

    # 2. Look up the Real User (by ID)
    try:
        user = User.objects.get(pk=name)
    except (ValueError, User.DoesNotExist):
        # Fallback: Try the old service lookup for legacy IDs
        tech = ticket_service.get_technician_details(name)
        if tech:
            return render(request, 'service_desk/technician_profile.html', {'technician': tech})
        messages.error(request, "Technician not found.")
        return redirect('manager_dashboard')

    # 3. Calculate Real Stats
    resolved_qs = Ticket.objects.filter(technician=user, status__in=['Resolved', 'Closed'])
    
    # Avg Resolution Calculation
    avg_res_str = "N/A"
    if resolved_qs.filter(closed_at__isnull=False).exists():
        avg_duration = resolved_qs.filter(closed_at__isnull=False).aggregate(t=Avg(F('closed_at') - F('created_at')))['t']
        if avg_duration:
            hours = avg_duration.total_seconds() / 3600
            if hours < 1:
                avg_res_str = f"{int(hours * 60)} mins"
            else:
                avg_res_str = f"{hours:.1f} hours"

    # 4. Avatar Logic: Respect prefer_initials setting
    if hasattr(user, 'profile') and user.profile.prefer_initials:
        # User prefers initials - always use UI Avatars
        avatar_url = f"https://ui-avatars.com/api/?name={user.first_name}+{user.last_name}&background=0D8ABC&color=fff"
    elif hasattr(user, 'profile') and user.profile.avatar:
        # User has an uploaded avatar and doesn't prefer initials
        avatar_url = user.profile.avatar.url
    else:
        # Fallback to UI Avatars (initials)
        avatar_url = f"https://ui-avatars.com/api/?name={user.first_name}+{user.last_name}&background=0D8ABC&color=fff"

    # 5. Profile Data Construction (with new fields)
    profile = getattr(user, 'profile', None)
    
    tech_data = {
        'id': user.id,
        'name': user.get_full_name() or user.username,
        'title': profile.title if profile else 'IT Support',
        'role': profile.title if profile else 'IT Support',
        'company': profile.company if profile else 'PRIME AE Group, Inc.',
        'manager_name': profile.manager_name if profile else '',
        'location': profile.location if profile else 'Remote',
        'email': user.email,
        'phone': profile.phone_office if profile else '',
        'avatar': avatar_url,
        'stats': {
            'open_tickets': Ticket.objects.filter(technician=user).exclude(status__in=['Resolved', 'Closed', 'Cancelled']).count(),
            'resolved_this_month': resolved_qs.count(),
            'avg_response': avg_res_str,
            'csat_score': '4.8/5'  # Placeholder until CSAT model is fully linked
        },
        'recent_activity': list(Ticket.objects.filter(technician=user).order_by('-updated_at')[:5].values_list('title', flat=True)),
        'feedback': []  # Placeholder for CSAT feedback
    }

    return render(request, 'service_desk/technician_profile.html', {'technician': tech_data})


@user_passes_test(lambda u: u.is_superuser)
def csat_report(request, tech_id=None):
    stats = ticket_service.get_dashboard_stats()
    csat_data = stats.get('csat_breakdown', {})
    if tech_id:
        csat_data = csat_data.get(tech_id, {})
    return render(request, 'service_desk/csat_report.html', {
        'csat_data': csat_data,
        'tech_id': tech_id
    })


# ============================================================================
# KNOWLEDGE BASE VIEWER (Single Article Detail - CLEAN VERSION)
# ============================================================================

@login_required
def kb_home(request):
    search_query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '').strip()
    
    articles = Article.objects.filter(status='Approved').order_by('-id')

    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(problem__icontains=search_query) |
            Q(solution__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(subcategory__icontains=search_query)
        )

    if category_filter and category_filter != 'All':
        articles = articles.filter(category=category_filter)

    recent_articles = articles[:10]

    return render(request, 'knowledge_base/kb_home.html', {
        'articles': articles,
        'recent_articles': recent_articles,
        'search_query': search_query,
        'current_category': category_filter
    })


@login_required
def article_detail(request, article_id=None, pk=None):
    lookup_id = article_id if article_id is not None else pk
    article = get_object_or_404(Article, pk=lookup_id)
    return render(request, 'knowledge_base/article_detail.html', {'article': article})


# ============================================================================
# KNOWLEDGE BASE MANAGER (ADMIN TABLE)
# ============================================================================

@user_passes_test(lambda u: u.is_superuser)
def kb_manager(request):
    search_query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '').strip()
    status_filter = request.GET.get('status', '').strip()
    sort_by = request.GET.get('sort', 'id').strip()

    # Fetch all category names for the dropdown
    categories = KBCategory.objects.values_list('name', flat=True).order_by('name')

    articles = Article.objects.all()

    total_count = articles.count()
    draft_count = articles.filter(status='Draft').count()
    pending_count = articles.filter(status__in=['Pending Approval', 'Pending']).count()

    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(problem__icontains=search_query) |
            Q(solution__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(subcategory__icontains=search_query)
        )
    
    if category_filter and category_filter != 'All':
        articles = articles.filter(category=category_filter)
        
    if status_filter:
        if status_filter == 'Draft':
            articles = articles.filter(status='Draft')
        elif status_filter in ['Pending', 'Pending Approval']:
            articles = articles.filter(status__in=['Pending Approval', 'Pending'])
        elif status_filter == 'Approved':
            articles = articles.filter(status='Approved')

    if sort_by == 'id':
        articles = articles.order_by('id')
    elif sort_by == '-id':
        articles = articles.order_by('-id')
    else:
        articles = articles.order_by('-updated_at')

    # HTMX: If this is an HTMX request, only return the KB table partial
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'knowledge_base/partials/kb_table.html', {
            'articles': articles,
            'total_count': total_count,
            'draft_count': draft_count,
            'pending_count': pending_count,
            'search_query': search_query,
            'current_category': category_filter,
            'current_sort': sort_by,
            'current_status': status_filter,
            'categories': categories,
        })
    return render(request, 'knowledge_base/kb_manager.html', {
        'articles': articles,
        'total_count': total_count,
        'draft_count': draft_count,
        'pending_count': pending_count,
        'search_query': search_query,
        'current_category': category_filter,
        'current_sort': sort_by,
        'current_status': status_filter,
        'categories': categories,
    })


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
    return render(request, 'knowledge_base/kb_form.html', {
        'form': form,
        'form_title': 'Create Knowledge Base Article',
        'submit_text': 'Create Article'
    })


@user_passes_test(lambda u: u.is_superuser)
def kb_edit(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    if request.method == 'POST':
        form = KBArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            try:
                 LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(Article).pk,
                    object_id=article.id,
                    object_repr=article.title,
                    action_flag=CHANGE,
                    change_message="Updated via KB Editor"
                )
            except: 
                pass
            messages.success(request, "Article updated successfully.")
            return redirect('article_detail', article_id=article.id)
    else:
        form = KBArticleForm(instance=article)
    
    return render(request, 'knowledge_base/kb_form.html', {'form': form, 'article': article})


@user_passes_test(lambda u: u.is_superuser)
def kb_delete(request, article_id):
    if request.method == 'POST':
        result = ticket_service.delete_kb_article(article_id, user=request.user.username)
        if result:
            messages.success(request, "Article deleted successfully.")
        else:
            messages.error(request, "Article not found.")
    return redirect('kb_manager')


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
        article_ids = [int(id) for id in selected_ids]
        
        if action == 'delete':
            deleted_count, _ = Article.objects.filter(id__in=article_ids).delete()
            messages.success(request, f"Successfully deleted {deleted_count} article(s).")

        else:
            status_map = {
                'approve': 'Approved',
                'draft': 'Draft',
                'pending': 'Pending Approval'
            }
            new_status = status_map.get(action)
            if new_status:
                updated_count = Article.objects.filter(id__in=article_ids).update(status=new_status)
                messages.success(request, f"Successfully moved {updated_count} article(s) to '{new_status}'.")
            else:
                messages.warning(request, f"Unknown action: {action}")

    except Exception as e:
        messages.error(request, f"Error during bulk action: {e}")

    return redirect('kb_manager')


# ============================================================================
# SYSTEM LOGS
# ============================================================================

@user_passes_test(lambda u: u.is_superuser)
def system_logs(request):
    # 1. Define Timezones
    NA_TIMEZONES = [
        ('America/New_York', 'Eastern Time (ET)'),
        ('America/Chicago', 'Central Time (CT)'),
        ('America/Denver', 'Mountain Time (MT)'),
        ('America/Los_Angeles', 'Pacific Time (PT)'),
        ('America/Anchorage', 'Alaska Time (AKT)'),
        ('Pacific/Honolulu', 'Hawaii-Aleutian Time (HST)'),
    ]

    # 2. Get Params
    selected_tz = request.GET.get('timezone', 'America/New_York')
    search_query = request.GET.get('q', '').strip()
    sort_param = request.GET.get('sort', '-timestamp')
    date_range = request.GET.get('range', '7d') # Default to 7 days
    
    # Activate Timezone for Display
    try:
        timezone.activate(selected_tz)
    except:
        timezone.activate('America/New_York')

    # 3. Calculate Date Range (Server Time)
    now = timezone.now()
    start_date = now - timedelta(days=7)
    end_date = now
    
    # Custom Start/End strings for the inputs
    custom_start_str = request.GET.get('start_date', '')
    custom_end_str = request.GET.get('end_date', '')

    if date_range == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == 'yesterday':
        yesterday = now - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif date_range == '7d':
        start_date = now - timedelta(days=7)
        end_date = now
    elif date_range == '30d':
        start_date = now - timedelta(days=30)
        end_date = now
    elif date_range == 'custom':
        if custom_start_str and custom_end_str:
            try:
                # Parse YYYY-MM-DD inputs
                s_dt = datetime.strptime(custom_start_str, '%Y-%m-%d')
                e_dt = datetime.strptime(custom_end_str, '%Y-%m-%d')
                # Make them aware (using current active timezone logic or server default)
                current_tz = timezone.get_current_timezone()
                start_date = timezone.make_aware(s_dt, current_tz)
                end_date = timezone.make_aware(e_dt, current_tz).replace(hour=23, minute=59, second=59)
            except ValueError:
                pass # Fallback to default if parse fails

    # 4. Fetch All Logs & Process
    logs = ticket_service.get_system_logs()
    processed_logs = []
    
    for log in logs:
        entry = log.copy()
        if 'timestamp' in entry:
            dt = parse_datetime(entry['timestamp'])
            if dt:
                if dt.tzinfo is None:
                    dt = pytz.utc.localize(dt)
                entry['dt_obj'] = dt
            else:
                entry['dt_obj'] = timezone.now()
        processed_logs.append(entry)

    # 5. Filter by Date
    # Note: ensure we compare aware datetimes
    filtered_logs = []
    for log in processed_logs:
        log_dt = log.get('dt_obj')
        if log_dt and start_date <= log_dt <= end_date:
            filtered_logs.append(log)

    # 6. Filter by Search Query
    if search_query:
        query = search_query.lower()
        filtered_logs = [
            l for l in filtered_logs
            if query in str(l.get('user', '')).lower()
            or query in str(l.get('action', '')).lower()
            or query in str(l.get('target', '')).lower()
            or query in str(l.get('details', '')).lower()
        ]

    # 7. Sort
    reverse = sort_param.startswith('-')
    sort_key = sort_param.lstrip('-')
    key_map = {'timestamp': 'timestamp', 'user': 'user', 'action': 'action'}
    dict_key = key_map.get(sort_key, 'timestamp')
    
    try:
        filtered_logs.sort(key=lambda x: x.get(dict_key, ''), reverse=reverse)
    except:
        pass 

    # 8. Context
    context = {
        'logs': filtered_logs,
        'na_timezones': NA_TIMEZONES,
        'selected_tz': selected_tz,
        'search_query': search_query,
        'current_sort': sort_param,
        # New Date Context
        'current_range': date_range,
        'start_date': custom_start_str,
        'end_date': custom_end_str,
    }
    
    # HTMX: If this is an HTMX request, only return the logs table partial
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'service_desk/partials/logs_table.html', context)
    return render(request, 'service_desk/system_logs.html', context)


# ============================================================================
# USER PROFILE & SETTINGS
# ============================================================================

@login_required
def my_profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        avatar = request.FILES.get('avatar')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        if avatar:
            user.profile.avatar = avatar
            user.profile.save()
            messages.success(request, "Profile updated successfully with new avatar.")
        else:
            messages.success(request, "Profile updated successfully.")
        
        return redirect('my_profile')

    return render(request, 'service_desk/my_profile.html')


# ============================================================================
# SITE CONFIGURATION (ADMIN ONLY)
# ============================================================================

@user_passes_test(lambda u: u.is_superuser)
def site_configuration(request):
    config = GlobalSettings.load()
    
    if request.method == 'POST':
        form = GlobalSettingsForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            ticket_service.log_system_event(
                user=request.user.username,
                action='Updated Site Configuration',
                target='Global Settings',
                details='Updated global configuration toggles'
            )
            messages.success(request, '✅ Site configuration updated successfully!')
            return redirect('site_configuration')
    else:
        form = GlobalSettingsForm(instance=config)
    
    categories = KBCategory.objects.prefetch_related('subcategories').order_by('sort_order', 'name')
    
    return render(request, 'service_desk/site_configuration.html', {
        'form': form,
        'config': config,
        'categories': categories,
    })


# ============================================================================
# USER MANAGEMENT (ADMIN ONLY)
# ============================================================================

@user_passes_test(lambda u: u.is_superuser)
def user_management(request):
    users = User.objects.all().order_by('username')
    return render(request, 'service_desk/user_management.html', {'users': users})


@user_passes_test(lambda u: u.is_superuser)
def user_add(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            try:
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(User).pk,
                    object_id=user.id,
                    object_repr=user.username,
                    action_flag=ADDITION,
                    change_message="Created via Service Portal"
                )
            except:
                pass
            messages.success(request, f'✅ User "{user.username}" created successfully.')
            return redirect('user_management')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'service_desk/user_form.html', {'form': form, 'title': 'Add New User'})


@user_passes_test(lambda u: u.is_superuser)
def user_edit(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if request.method == 'POST' and 'delete_user' in request.POST:
        username = user_obj.username
        try:
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(User).pk,
                object_id=user_obj.id,
                object_repr=username,
                action_flag=DELETION,
                change_message="Deleted via Service Portal"
            )
        except:
            pass

        user_obj.delete()
        messages.success(request, f'✅ User "{username}" has been deleted.')
        return redirect('user_management')

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user_obj)
        if form.is_valid():
            form.save()
            try:
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(User).pk,
                    object_id=user_obj.id,
                    object_repr=user_obj.username,
                    action_flag=CHANGE,
                    change_message="Modified via Service Portal"
                )
            except:
                pass
            messages.success(request, f'✅ User "{user_obj.username}" updated successfully.')
            return redirect('user_management')
    else:
        form = CustomUserChangeForm(instance=user_obj)

    return render(request, 'service_desk/user_form.html', {'form': form, 'user_obj': user_obj, 'title': f'Edit User: {user_obj.username}'})


# ============================================================================
# KB TAXONOMY MANAGEMENT
# ============================================================================

@user_passes_test(lambda u: u.is_superuser)
def kb_category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            KBCategory.objects.create(name=name)
            messages.success(request, f"✅ Category '{name}' created.")
        else:
            messages.error(request, "Category name is required.")
    return redirect('site_configuration')


@user_passes_test(lambda u: u.is_superuser)
def kb_category_delete(request, category_id):
    if request.method == 'POST':
        try:
            cat = KBCategory.objects.get(id=category_id)
            if cat.articles.exists():
                fallback, created = KBCategory.objects.get_or_create(
                    name='Uncategorized',
                    defaults={'sort_order': 999}
                )
                cat.articles.update(category_fk=fallback)
                messages.warning(request, f"⚠️ Reassigned {cat.articles.count()} articles to 'Uncategorized'.")
            
            cat.delete()
            messages.success(request, f"✅ Category '{cat.name}' deleted.")
        except KBCategory.DoesNotExist:
            messages.error(request, "Category not found.")
    return redirect('site_configuration')


@user_passes_test(lambda u: u.is_superuser)
def kb_subcategory_add(request):
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        name = request.POST.get('name')
        if parent_id and name:
            try:
                parent = KBCategory.objects.get(id=parent_id)
                KBSubcategory.objects.create(parent=parent, name=name)
                messages.success(request, f"✅ Subcategory '{name}' added to '{parent.name}'.")
            except KBCategory.DoesNotExist:
                messages.error(request, "Parent category not found.")
        else:
            messages.error(request, "Parent category and name are required.")
    return redirect('site_configuration')


@user_passes_test(lambda u: u.is_superuser)
def kb_subcategory_delete(request, subcategory_id):
    if request.method == 'POST':
        try:
            subcat = KBSubcategory.objects.get(id=subcategory_id)
            subcat.delete()
            messages.success(request, f"✅ Subcategory '{subcat.name}' deleted.")
        except KBSubcategory.DoesNotExist:
            messages.error(request, "Subcategory not found.")
    return redirect('site_configuration')


@require_POST
def kb_update_status(request, pk):
    if not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()

    with transaction.atomic():
        article = get_object_or_404(Article.objects.select_for_update(), pk=pk)
        new_status = request.POST.get('status')
        if new_status in ['Draft', 'Pending', 'Approved']:
            article.status = new_status
            article.save()

    return redirect('article_detail', article_id=pk)
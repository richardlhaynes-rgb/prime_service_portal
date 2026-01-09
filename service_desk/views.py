from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.views.decorators.http import require_POST
import re
import sys

from .forms import (
    ApplicationIssueForm, EmailMailboxForm, HardwareIssueForm, PrinterScannerForm,
    SoftwareInstallForm, GeneralQuestionForm, VPResetForm, VPPermissionsForm,
    TicketReplyForm, KBArticleForm, GlobalSettingsForm, CustomUserCreationForm, CustomUserChangeForm, AgentTicketForm
)

from .models import (
    Ticket, Comment, GlobalSettings, Notification, UserProfile, 
    CSATSurvey, ServiceBoard, ServiceType, ServiceSubtype, ServiceItem
)

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
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from services.ticket_service import log_system_event
import os

from inventory.models import HardwareAsset
from knowledge_base.models import Article
from django.core.paginator import Paginator

# ============================================================================
# USER DASHBOARD
# ============================================================================

@login_required
def dashboard(request):
    # UPDATED: Added select_related/prefetch_related for Technician & Collaborators
    user_tickets = Ticket.objects.filter(submitter=request.user).select_related('technician', 'technician__profile').prefetch_related('collaborators').order_by('-created_at')
    
    open_statuses = ['New', 'User Commented', 'Work In Progress', 'Reopened', 'Assigned', 'In Progress', 'Awaiting User Reply', 'On Hold']
    resolved_statuses = ['Resolved', 'Cancelled']
    
    open_tickets = user_tickets.filter(status__in=open_statuses).count()
    resolved_tickets = user_tickets.filter(status__in=resolved_statuses).count()
    total_tickets = user_tickets.count()
    
    feedback_ticket = Ticket.objects.filter(
        submitter=request.user,
        status='Resolved'
    ).filter(
        survey__isnull=True
    ).order_by('-updated_at').first()
    
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

@login_required
def dashboard_stats(request):
    user_tickets = Ticket.objects.filter(submitter=request.user)
    
    open_statuses = ['New', 'User Commented', 'Work In Progress', 'Reopened', 'Assigned', 'In Progress', 'Awaiting User Reply', 'On Hold']
    resolved_statuses = ['Resolved', 'Cancelled']
    
    open_tickets = user_tickets.filter(status__in=open_statuses).count()
    resolved_tickets = user_tickets.filter(status__in=resolved_statuses).count()
    total_tickets = user_tickets.count()
    
    return render(request, 'service_desk/partials/dashboard_stats.html', {
        'open_tickets': open_tickets,
        'resolved_tickets': resolved_tickets,
        'total_tickets': total_tickets,
    })

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
        else:
            recommended_articles = sorted(articles, key=lambda a: a.get('updated_at', ''), reverse=True)[:3]

    return render(request, 'service_desk/service_catalog.html', {
        'recommended_articles': recommended_articles
    })

# ============================================================================
# TICKET SUBMISSION FORMS
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
                status=Ticket.Status.NEW,
                attachment=request.FILES.get('screenshot'),
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
            if device == 'Other' and data.get('other_device'):
                device = f'Other ({data["other_device"]})'
            title = f'[Portal] Hardware Issue: {device} - {data["summary"]}'
            desc = f'USER REPORT:\n-----------------\nDevice: {device}\nSerial/Tag: {data.get("device_serial", "N/A")}\n\nDETAILS:\n{data["description"]}'
            Ticket.objects.create(
                title=title,
                description=desc,
                ticket_type=Ticket.TicketType.HARDWARE,
                submitter=request.user,
                priority=Ticket.Priority.P2 if data.get('is_urgent') else Ticket.Priority.P3,
                status=Ticket.Status.NEW,
                attachment=request.FILES.get('screenshot'),
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
                status=Ticket.Status.NEW,
                attachment=request.FILES.get('screenshot'),
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
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        form = TicketReplyForm(request.POST)
        changes_made = False
        action_summary = []
        
        # --- 1. Collaborators Update (New) ---
        # Get list of IDs from the multiple hidden inputs named 'collaborators'
        new_collab_ids = request.POST.getlist('collaborators')
        # Convert to integers for comparison
        new_collab_ids = [int(id) for id in new_collab_ids if id.isdigit()]
        
        # Get current IDs
        current_collab_ids = list(ticket.collaborators.values_list('id', flat=True))
        
        # Compare sorted lists to see if change occurred
        if sorted(new_collab_ids) != sorted(current_collab_ids):
            # Update the Many-to-Many relationship
            ticket.collaborators.set(new_collab_ids)
            action_summary.append("collaborators updated")
            changes_made = True

        # --- 2. Standard Field Updates ---
        if request.POST.get('reopen_ticket'):
            ticket.status = 'Reopened'
            ticket.closed_at = None
            action_summary.append('ticket reopened')
            changes_made = True
            Comment.objects.create(
                ticket=ticket,
                author=request.user,
                text=f"Ticket reopened by {request.user.get_full_name() or request.user.username}.",
                is_internal=True
            )

        elif request.POST.get('close_ticket'):
            ticket.status = 'Resolved'
            ticket.closed_at = timezone.now()
            action_summary.append('ticket marked as Resolved')
            changes_made = True
            
            if not ticket.technician:
                ticket.technician = request.user
                action_summary.append(f'assigned to {request.user.get_full_name()}')
            
            Comment.objects.create(
                ticket=ticket,
                author=request.user,
                text=f"Ticket closed by {request.user.get_full_name() or request.user.username}.",
                is_internal=True
            )

        new_status = request.POST.get('status')
        if new_status and new_status != ticket.status and not (request.POST.get('close_ticket') or request.POST.get('reopen_ticket')):
            ticket.status = new_status
            action_summary.append(f"status updated to {new_status}")
            changes_made = True
            if new_status in ['Resolved', 'Closed', 'Cancelled']:
                ticket.closed_at = timezone.now()
            elif new_status in ['New', 'Reopened', 'In Progress']:
                ticket.closed_at = None

        new_priority = request.POST.get('priority')
        if new_priority and new_priority != ticket.priority:
            ticket.priority = new_priority
            action_summary.append(f"priority updated to {new_priority}")
            changes_made = True

        new_tech_id = request.POST.get('technician')
        if new_tech_id is not None:
            if new_tech_id == "":
                if ticket.technician:
                    ticket.technician = None
                    action_summary.append("technician unassigned")
                    changes_made = True
            elif str(ticket.technician_id) != new_tech_id:
                ticket.technician_id = int(new_tech_id)
                action_summary.append("technician updated")
                changes_made = True

        new_board_id = request.POST.get('board')
        if new_board_id and str(ticket.board_id) != new_board_id:
            ticket.board_id = int(new_board_id)
            action_summary.append("board moved")
            changes_made = True

        if form.is_valid():
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
                    ticket.save()

        if changes_made:
            ticket.save()
            message = f"Ticket updated: {', '.join(action_summary)}."
            if not request.headers.get('HX-Request'):
                messages.success(request, message)
        
        if request.headers.get('HX-Request'):
            updated_comments = ticket.comments.all().order_by('created_at')
            return render(request, 'service_desk/partials/ticket_activities.html', {
                'comments': updated_comments, 
                'request': request
            })

        return redirect('ticket_detail', ticket_id=ticket_id)

    comments = ticket.comments.all().order_by('created_at')
    form = TicketReplyForm(initial={'priority': ticket.priority})
    
    if ticket.attachment:
        ticket.filename = os.path.basename(ticket.attachment.name)

    technicians = User.objects.filter(groups__name='Service Desk') 
    boards = ServiceBoard.objects.filter(is_active=True)
    status_choices = Ticket.Status.choices
    
    # Pre-fetch collaborators for the JS widget
    current_collaborators = [
        {
            'id': u.id,
            'name': u.get_full_name(),
            'avatar': u.profile.avatar.url if u.profile.avatar else f"https://ui-avatars.com/api/?name={u.first_name}+{u.last_name}&background=0D8ABC&color=fff"
        } 
        for u in ticket.collaborators.all()
    ]

    context = {
        'ticket': ticket,
        'comments': comments,
        'form': form,
        'technicians': technicians,
        'boards': boards,
        'status_choices': status_choices,
        'current_collaborators_json': json.dumps(current_collaborators), # Pass as JSON for Alpine
        'is_demo_mode': False,
    }
    
# 1. Pre-fetch Collaborators for JS
    current_collaborators = [
        {
            'id': u.id,
            'name': u.get_full_name(),
            'avatar': u.profile.avatar.url if u.profile.avatar else f"https://ui-avatars.com/api/?name={u.first_name}+{u.last_name}&background=0D8ABC&color=fff"
        } 
        for u in ticket.collaborators.all()
    ]

    # 2. Pre-fetch Technician for JS (NEW)
    current_tech = None
    if ticket.technician:
        u = ticket.technician
        current_tech = {
            'id': u.id,
            'name': u.get_full_name(),
            'avatar': u.profile.avatar.url if u.profile.avatar else f"https://ui-avatars.com/api/?name={u.first_name}+{u.last_name}&background=0D8ABC&color=fff"
        }

    context = {
        'ticket': ticket,
        'comments': comments,
        'form': form,
        'technicians': technicians,
        'boards': boards,
        'status_choices': status_choices,
        'current_collaborators_json': json.dumps(current_collaborators),
        'current_tech_json': json.dumps(current_tech) if current_tech else 'null', # Pass Tech as JSON
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
    date_range = request.GET.get('range', '7d')
    now = timezone.now()
    
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

    tickets = Ticket.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
    total_tickets = tickets.count()

    resolved = tickets.filter(status__in=['Resolved', 'Closed'], closed_at__isnull=False)
    
    if resolved.exists():
        avg = resolved.aggregate(t=Avg(F('closed_at') - F('created_at')))['t']
        avg_resolution_time = f"{avg.total_seconds()/3600:.1f} hours" if avg else "0 hours"
    else:
        avg_resolution_time = "0 hours"
        
    responded = tickets.filter(first_response_at__isnull=False)
    if responded.exists():
        avg = responded.aggregate(t=Avg(F('first_response_at') - F('created_at')))['t']
        first_response_time = f"{int(avg.total_seconds()/60)} mins" if avg else "N/A"
    else:
        first_response_time = "N/A"
        
    priority_escalations = tickets.filter(priority__icontains='Critical').exclude(status__in=['Resolved', 'Closed']).count()
    
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

    days_in_range = (end_date - start_date).days + 1
    trend_labels = []
    trend_data = []
    
    for i in range(days_in_range):
        current_day_start = start_date + timedelta(days=i)
        current_day_end = current_day_start + timedelta(days=1)
        
        if current_day_start > now:
            break
            
        if days_in_range <= 2:
            label = current_day_start.strftime('%b %d') 
        elif days_in_range <= 10:
            label = current_day_start.strftime('%a')
        else:
            label = current_day_start.strftime('%b %d')
            
        trend_labels.append(label)
        
        count = Ticket.objects.filter(created_at__gte=current_day_start, created_at__lt=current_day_end).count()
        trend_data.append(count)

    roster = []
    res_labels = []
    res_data = []
    
    service_desk = Group.objects.filter(name='Service Desk').first()
    if service_desk:
        for member in service_desk.user_set.all():
            open_count = Ticket.objects.filter(technician=member).exclude(status__in=['Resolved', 'Closed']).count()
            
            if hasattr(member, 'profile') and member.profile.prefer_initials:
                avatar = f"https://ui-avatars.com/api/?name={member.first_name}+{member.last_name}&background=random&color=fff"
            elif hasattr(member, 'profile') and member.profile.avatar:
                avatar = member.profile.avatar.url
            else:
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

    type_counts = tickets.values('type__name').annotate(c=Count('id')).order_by('-c')[:5]

    analytics = {
        'total_tickets': total_tickets,
        'avg_resolution_time': avg_resolution_time,
        'first_response_time': first_response_time,
        'priority_escalations': priority_escalations,
        'sla_breaches': sla_breaches,
        'volume_by_status': {'labels': list(vol_data.keys()), 'data': list(vol_data.values())},
        'tickets_by_type': {
            'labels': [x['type__name'] or 'Uncategorized' for x in type_counts], 
            'data': [x['c'] for x in type_counts]
        },
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
            url = request.POST.get(f'vendor_url_{i}', '') 
            if name:
                vendor_status.append({'name': name, 'status': status, 'url': url})

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
    try:
        user = User.objects.get(pk=name)
    except (ValueError, User.DoesNotExist):
        tech = ticket_service.get_technician_details(name)
        if tech:
            return render(request, 'service_desk/technician_profile.html', {'technician': tech})
        messages.error(request, "Technician not found.")
        return redirect('manager_dashboard')

    resolved_qs = Ticket.objects.filter(technician=user, status__in=['Resolved', 'Closed'])
    
    avg_res_str = "N/A"
    if resolved_qs.filter(closed_at__isnull=False).exists():
        avg_duration = resolved_qs.filter(closed_at__isnull=False).aggregate(t=Avg(F('closed_at') - F('created_at')))['t']
        if avg_duration:
            hours = avg_duration.total_seconds() / 3600
            if hours < 1:
                avg_res_str = f"{int(hours * 60)} mins"
            else:
                avg_res_str = f"{hours:.1f} hours"

    csat_avg = CSATSurvey.objects.filter(ticket__technician=user).aggregate(avg=Avg('rating'))['avg']
    csat_score_str = f"{csat_avg:.1f}/5" if csat_avg else "N/A"

    if hasattr(user, 'profile') and user.profile.prefer_initials:
        avatar_url = f"https://ui-avatars.com/api/?name={user.first_name}+{user.last_name}&background=0D8ABC&color=fff"
    elif hasattr(user, 'profile') and user.profile.avatar:
        avatar_url = user.profile.avatar.url
    else:
        avatar_url = f"https://ui-avatars.com/api/?name={user.first_name}+{user.last_name}&background=0D8ABC&color=fff"

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
            'csat_score': csat_score_str
        },
        'recent_activity': list(Ticket.objects.filter(technician=user).order_by('-updated_at')[:5].values_list('title', flat=True)),
        'feedback': [] 
    }

    return render(request, 'service_desk/technician_profile.html', {'technician': tech_data})

# ============================================================================
# KNOWLEDGE BASE VIEWER
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
    
    if request.headers.get('HX-Request'):
        return render(request, 'knowledge_base/partials/kb_results.html', {
            'recent_articles': recent_articles
        })

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
# KNOWLEDGE BASE MANAGER
# ============================================================================

@user_passes_test(lambda u: u.is_superuser)
def kb_manager(request):
    search_query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '').strip()
    status_filter = request.GET.get('status', '').strip()
    sort_by = request.GET.get('sort', 'id').strip()

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
    NA_TIMEZONES = [
        ('America/New_York', 'Eastern Time (ET)'),
        ('America/Chicago', 'Central Time (CT)'),
        ('America/Denver', 'Mountain Time (MT)'),
        ('America/Los_Angeles', 'Pacific Time (PT)'),
        ('America/Anchorage', 'Alaska Time (AKT)'),
        ('Pacific/Honolulu', 'Hawaii-Aleutian Time (HST)'),
    ]

    selected_tz = request.GET.get('timezone', 'America/New_York')
    search_query = request.GET.get('q', '').strip()
    sort_param = request.GET.get('sort', '-timestamp')
    date_range = request.GET.get('range', '7d') 
    
    try:
        timezone.activate(selected_tz)
    except:
        timezone.activate('America/New_York')

    now = timezone.now()
    start_date = now - timedelta(days=7)
    end_date = now
    
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
                s_dt = datetime.strptime(custom_start_str, '%Y-%m-%d')
                e_dt = datetime.strptime(custom_end_str, '%Y-%m-%d')
                current_tz = timezone.get_current_timezone()
                start_date = timezone.make_aware(s_dt, current_tz)
                end_date = timezone.make_aware(e_dt, current_tz).replace(hour=23, minute=59, second=59)
            except ValueError:
                pass 

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

    filtered_logs = []
    for log in processed_logs:
        log_dt = log.get('dt_obj')
        if log_dt and start_date <= log_dt <= end_date:
            filtered_logs.append(log)

    if search_query:
        query = search_query.lower()
        filtered_logs = [
            l for l in filtered_logs
            if query in str(l.get('user', '')).lower()
            or query in str(l.get('action', '')).lower()
            or query in str(l.get('target', '')).lower()
            or query in str(l.get('details', '')).lower()
        ]

    reverse = sort_param.startswith('-')
    sort_key = sort_param.lstrip('-')
    key_map = {'timestamp': 'timestamp', 'user': 'user', 'action': 'action'}
    dict_key = key_map.get(sort_key, 'timestamp')
    
    try:
        filtered_logs.sort(key=lambda x: x.get(dict_key, ''), reverse=reverse)
    except:
        pass 

    context = {
        'logs': filtered_logs,
        'na_timezones': NA_TIMEZONES,
        'selected_tz': selected_tz,
        'search_query': search_query,
        'current_sort': sort_param,
        'current_range': date_range,
        'start_date': custom_start_str,
        'end_date': custom_end_str,
    }
    
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'service_desk/partials/logs_table.html', context)
    return render(request, 'service_desk/system_logs.html', context)

# ============================================================================
# USER PROFILE & SETTINGS
# ============================================================================

@login_required
def my_profile(request):
    user = request.user
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save()

            avatar_file = request.FILES.get('avatar')
            if avatar_file:
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.avatar = avatar_file
                profile.prefer_initials = False
                profile.save()

            messages.success(request, "Your profile has been updated.")
            return redirect('my_profile')
    else:
        form = CustomUserChangeForm(instance=user)

    if not user.is_superuser:
        allowed_fields = ['avatar', 'prefer_initials']
        for field_name, field in form.fields.items():
            if field_name not in allowed_fields:
                field.widget.attrs['disabled'] = 'disabled'
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{existing_classes} opacity-50 cursor-not-allowed".strip()

    context = {
        'form': form,
        'is_self_profile': True,
        'page_title': 'My Profile'
    }
    return render(request, 'service_desk/user_profile.html', context)

# ============================================================================
# SITE CONFIGURATION (ADMIN ONLY)
# ============================================================================

@user_passes_test(lambda u: u.is_superuser)
def site_configuration(request):
    config = GlobalSettings.load()

    form_class_options = [
        ('GeneralQuestionForm', 'General Question (Default)'),
        ('HardwareIssueForm', 'Hardware Issue'),
        ('PrinterScannerForm', 'Printer & Scanner Issue'),
        ('EmailMailboxForm', 'Email & Mailbox Help'),
        ('ApplicationIssueForm', 'Application Problem'),
        ('SoftwareInstallForm', 'Software Installation'),
        ('VPResetForm', 'Deltek VP Password Reset'),
        ('VPPermissionsForm', 'Deltek VP Permissions'),
    ]
    
    service_boards = ServiceBoard.objects.prefetch_related('restricted_groups', 'allowed_types').all().order_by('sort_order', 'name')
    service_types = ServiceType.objects.prefetch_related('boards', 'subtypes').all().order_by('name')
    service_subtypes = ServiceSubtype.objects.prefetch_related('parent_types', 'items').all().order_by('name')
    service_items = ServiceItem.objects.prefetch_related('parent_subtypes').all().order_by('name')
    
    categories = KBCategory.objects.prefetch_related('subcategories').all().order_by('name')
    
    all_groups = Group.objects.all().order_by('name')
    
    form = GlobalSettingsForm(instance=config)

    if request.method == 'POST':
        active_tab = request.POST.get('active_tab', 'general')
        action = request.POST.get('action')

        if action == 'create_board':
            name = request.POST.get('name')
            if name:
                ServiceBoard.objects.get_or_create(name=name, defaults={'sort_order': 99})
                messages.success(request, f"Board '{name}' created.")
            return redirect(f"{request.path}?tab=boards")
            
        elif action == 'update_board':
            board = get_object_or_404(ServiceBoard, id=request.POST.get('board_id'))
            board.name = request.POST.get('name')
            board.description = request.POST.get('description')
            board.restricted_groups.set(request.POST.getlist('groups'))
            board.save()
            messages.success(request, f"Board '{board.name}' updated.")
            return redirect(f"{request.path}?tab=boards")

        elif action == 'delete_board':
            board = get_object_or_404(ServiceBoard, id=request.POST.get('board_id'))
            board.delete()
            messages.success(request, "Board deleted.")
            return redirect(f"{request.path}?tab=boards")

        elif action == 'create_type':
            name = request.POST.get('name')
            form_class = request.POST.get('form_class', 'GeneralQuestionForm')
            if name:
                new_type = ServiceType.objects.create(name=name, form_class_name=form_class)
                board_ids = request.POST.getlist('assigned_boards')
                new_type.boards.set(board_ids)
                messages.success(request, f"Type '{name}' created.")
            return redirect(f"{request.path}?tab=service-taxonomy&subtab=types")

        elif action == 'update_type':
            obj = get_object_or_404(ServiceType, id=request.POST.get('type_id'))
            obj.name = request.POST.get('name')
            obj.form_class_name = request.POST.get('form_class')
            obj.boards.set(request.POST.getlist('assigned_boards'))
            obj.save()
            messages.success(request, f"Type '{obj.name}' updated.")
            return redirect(f"{request.path}?tab=service-taxonomy&subtab=types")

        elif action == 'delete_type':
            ServiceType.objects.filter(id=request.POST.get('type_id')).delete()
            messages.success(request, "Type deleted.")
            return redirect(f"{request.path}?tab=service-taxonomy&subtab=types")

        elif action == 'create_subtype':
            name = request.POST.get('name')
            if name:
                new_sub = ServiceSubtype.objects.create(name=name)
                new_sub.parent_types.set(request.POST.getlist('parent_types'))
                messages.success(request, f"Subtype '{name}' created.")
            return redirect(f"{request.path}?tab=service-taxonomy&subtab=subtypes")

        elif action == 'update_subtype':
            obj = get_object_or_404(ServiceSubtype, id=request.POST.get('subtype_id'))
            obj.name = request.POST.get('name')
            obj.parent_types.set(request.POST.getlist('parent_types'))
            obj.save()
            messages.success(request, f"Subtype '{obj.name}' updated.")
            return redirect(f"{request.path}?tab=service-taxonomy&subtab=subtypes")

        elif action == 'delete_subtype':
            ServiceSubtype.objects.filter(id=request.POST.get('subtype_id')).delete()
            messages.success(request, "Subtype deleted.")
            return redirect(f"{request.path}?tab=service-taxonomy&subtab=subtypes")

        elif action == 'create_item':
            name = request.POST.get('name')
            if name:
                new_item = ServiceItem.objects.create(name=name)
                new_item.parent_subtypes.set(request.POST.getlist('parent_subtypes'))
                messages.success(request, f"Item '{name}' created.")
            return redirect(f"{request.path}?tab=service-taxonomy&subtab=items")

        elif action == 'update_item':
            obj = get_object_or_404(ServiceItem, id=request.POST.get('item_id'))
            obj.name = request.POST.get('name')
            obj.parent_subtypes.set(request.POST.getlist('parent_subtypes'))
            obj.save()
            messages.success(request, f"Item '{obj.name}' updated.")
            return redirect(f"{request.path}?tab=service-taxonomy&subtab=items")

        elif action == 'delete_item':
            ServiceItem.objects.filter(id=request.POST.get('item_id')).delete()
            messages.success(request, "Item deleted.")
            return redirect(f"{request.path}?tab=service-taxonomy&subtab=items")

        elif request.POST.get('save_settings'):
            form = GlobalSettingsForm(request.POST, instance=config)
            if form.is_valid():
                form.save()
            messages.success(request, "Settings updated.")
            return redirect('site_configuration')

    active_tab = request.GET.get('tab', 'general')
    active_subtab = request.GET.get('subtab', 'types')

    context = {
        'site_config': config,
        'form': form,
        'active_tab': active_tab,
        'active_subtab': active_subtab,
        'service_boards': service_boards,
        'service_types': service_types,
        'service_subtypes': service_subtypes,
        'service_items': service_items,
        'categories': categories,
        'all_groups': all_groups,
        'form_class_options': form_class_options,
    }
    return render(request, 'service_desk/site_configuration.html', context)

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
        form = CustomUserChangeForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            
            if not user.password:
                user.set_unusable_password()
            
            user.save()
            
            avatar_file = request.FILES.get('avatar')
            
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            if avatar_file:
                profile.avatar = avatar_file
                profile.prefer_initials = False
                profile.save()

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
        form = CustomUserChangeForm()
    
    return render(request, 'service_desk/user_profile.html', {
        'form': form, 
        'title': 'Add New User',
        'is_new_user': True 
    })


@user_passes_test(lambda u: u.is_superuser)
def user_edit(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST' and 'delete_user' in request.POST:
        if target_user == request.user:
             messages.error(request, "You cannot delete your own account while logged in.")
             return redirect('user_edit', user_id=user_id)
        
        username = target_user.username
        target_user.delete()
        log_system_event(
             user=request.user,
             action="User Deleted",
             target=username, 
             details=f"Deleted user account: {username}"
        )
        messages.success(request, f"User '{username}' has been deleted.")
        return redirect('user_management')

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=target_user)
        if form.is_valid():
            user = form.save()
            
            avatar_file = request.FILES.get('avatar')
            if avatar_file:
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.avatar = avatar_file
                profile.prefer_initials = False
                profile.save()
            
            log_system_event(
                user=request.user.username,
                action="User Updated",
                target=user.username,
                details=f"Updated profile for user: {user.username}"
            )
            messages.success(request, f"User '{user.username}' has been updated.")
            return redirect('user_management')
    else:
        form = CustomUserChangeForm(instance=target_user)

    context = {
        'form': form,
        'target_user': target_user,
        'is_self_profile': (target_user == request.user),
        'page_title': f'Edit User: {target_user.username}'
    }
    return render(request, 'service_desk/user_profile.html', context)

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

# ============================================================================
# NOTIFICATIONS
# ============================================================================

@login_required
def get_notifications(request):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(request, 'service_desk/partials/notification_badge.html', {
        'unread_count': unread_count
    })

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'service_desk/partials/notification_list.html', {
        'notifications': notifications
    })

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, 'service_desk/partials/notification_list.html', {
        'notifications': []
    })

@login_required
def mark_notification_read(request, notification_id):
    from .models import Notification
    from django.urls import NoReverseMatch
    
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    
    target = notification.link
    
    if not target or target == '#' or target == 'None':
        messages.warning(request, "This notification was just an informational alert (no specific page attached).")
        return redirect('dashboard')
        
    try:
        if target and target.startswith('/ticket/'):
            import re
            match = re.search(r'/ticket/(\d+)/', target)
            if match:
                ticket_id = match.group(1)
                return redirect('ticket_detail', ticket_id=ticket_id)
        
        return redirect(target)
    except (NoReverseMatch, Exception):
        messages.error(request, "We couldn't take you to that specific page (the link might be outdated), so here is your Dashboard.")
        return redirect('dashboard')

@login_required
def notification_history(request):
    from .models import Notification
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'service_desk/notification_history.html', {
        'notifications': notifications
    })

@login_required
@require_POST
def notification_bulk_action(request):
    from .models import Notification
    
    action = request.POST.get('action')
    selected_ids = request.POST.getlist('selected_ids')
    
    if not selected_ids:
        messages.warning(request, "No notifications selected.")
        return redirect('notification_history')

    qs = Notification.objects.filter(id__in=selected_ids, user=request.user)
    count = qs.count()

    if action == 'mark_unread':
        qs.update(is_read=False)
        messages.success(request, f"Marked {count} notifications as unread.")
    elif action == 'mark_read':
        qs.update(is_read=True)
        messages.success(request, f"Marked {count} notifications as read.")

    return redirect('notification_history')


@login_required
@require_POST
def delete_notifications(request):
    notification_ids = request.POST.getlist('selected_ids')
    if notification_ids:
        Notification.objects.filter(
            id__in=notification_ids, 
            user=request.user
        ).delete()
        messages.success(request, f"{len(notification_ids)} notification(s) deleted.")
    else:
        messages.warning(request, "No notifications selected.")
        
    return redirect('notification_history')

# ============================================================================
# TECHNICIAN WORKSPACE
# ============================================================================

@login_required
@user_passes_test(lambda u: u.is_staff)
def workspace(request):
    all_boards = ServiceBoard.objects.filter(is_active=True)
    
    selected_board_ids = request.GET.get('boards', '').split(',')
    selected_board_ids = [int(id) for id in selected_board_ids if id.isdigit()]
    
    if not selected_board_ids:
        user_boards = all_boards.filter(members=request.user)
        if user_boards.exists():
            selected_board_ids = list(user_boards.values_list('id', flat=True))
        else:
            selected_board_ids = list(all_boards.values_list('id', flat=True))

    view_mode = request.GET.get('view', 'grid') 

    sort_param = request.GET.get('sort', 'created_at') 
    direction = request.GET.get('direction', 'desc')
    
    valid_sorts = {
        'id': 'id',
        'title': 'title',
        'board__name': 'board__name',
        'status': 'status',
        'submitter__first_name': 'submitter__first_name',
        'created_at': 'created_at',
        'technician__first_name': 'technician__first_name',
        'priority': 'priority'
    }
    
    db_sort_field = valid_sorts.get(sort_param, 'created_at')
    
    if direction == 'desc':
        db_sort_field = '-' + db_sort_field

    grid_tickets = Ticket.objects.filter(
        board__id__in=selected_board_ids
    ).exclude(
        status__in=['Resolved', 'Closed', 'Cancelled']
    ).select_related('submitter', 'technician', 'board').prefetch_related('collaborators').order_by(db_sort_field)

    # UPDATED: 'My Tickets' now includes tickets where user is Assignee OR Collaborator
    my_tickets = Ticket.objects.filter(
        Q(technician=request.user) | Q(collaborators=request.user)
    ).exclude(
        status__in=['Resolved', 'Closed', 'Cancelled']
    ).select_related('submitter', 'technician').prefetch_related('collaborators').order_by('-priority').distinct()
    
    kanban_new = my_tickets.filter(status__in=['New', 'Assigned', 'Reopened'])
    kanban_progress = my_tickets.filter(status__in=['In Progress', 'Work In Progress', 'Waiting on User'])
    kanban_done = Ticket.objects.filter(technician=request.user, status__in=['Resolved', 'Closed']).order_by('-updated_at')[:10]

    context = {
        'all_boards': all_boards,
        'selected_board_ids': selected_board_ids,
        'grid_tickets': grid_tickets,
        'view_mode': view_mode,
        'kanban_new': kanban_new,
        'kanban_progress': kanban_progress,
        'kanban_done': kanban_done,
    }

    return render(request, 'service_desk/workspace.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
@csrf_exempt
def workspace_update(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticket_id = data.get('ticket_id')
            new_status = data.get('new_status')
            
            ticket = Ticket.objects.get(id=ticket_id)
            
            if ticket.technician != request.user and not request.user.is_superuser:
                 return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=403)

            ticket.status = new_status
            
            if new_status == 'Resolved' and not ticket.closed_at:
                ticket.closed_at = timezone.now()
                
            ticket.save()
            return JsonResponse({'status': 'success'})
        except Ticket.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ticket not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'invalid method'}, status=400)

@user_passes_test(lambda u: u.is_superuser)
def manage_service_boards(request):
    boards = ServiceBoard.objects.all()
    if request.method == 'POST':
        pass
    return render(request, 'service_desk/admin_service_boards.html', {'boards': boards})

# ============================================================================
# CSAT REPORT
# ============================================================================

@user_passes_test(lambda u: u.is_superuser)
def csat_report(request, tech_id=None, pk=None, id=None, *args, **kwargs):
    from .models import CSATSurvey
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    target_id = tech_id or pk or id or kwargs.get('tech_id') or kwargs.get('pk') or kwargs.get('id')
    
    date_range = request.GET.get('range', '90d')
    now = timezone.now()
    
    start_date = now - timedelta(days=90)
    end_date = now + timedelta(days=1)

    if date_range == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_range == '7d':
        start_date = now - timedelta(days=7)
    elif date_range == '30d':
        start_date = now - timedelta(days=30)
    elif date_range == 'custom':
        try:
            s = request.GET.get('start')
            e = request.GET.get('end')
            if s and e:
                start_date = datetime.strptime(s, '%Y-%m-%d').replace(tzinfo=timezone.get_current_timezone())
                end_date = datetime.strptime(e, '%Y-%m-%d').replace(hour=23, minute=59, tzinfo=timezone.get_current_timezone())
        except:
            pass

    surveys = CSATSurvey.objects.filter(
        submitted_at__gte=start_date, 
        submitted_at__lte=end_date
    ).select_related('ticket', 'submitted_by', 'ticket__technician').order_by('-submitted_at')

    technician = None
    if target_id:
        surveys = surveys.filter(ticket__technician__id=target_id)
        user_obj = get_object_or_404(User, pk=target_id)
        
        technician = {
            'name': user_obj.get_full_name() or user_obj.username,
            'id': user_obj.id
        }

    feedback_list = []
    for s in surveys:
        user_obj = s.submitted_by
        avatar_url = None
        
        if user_obj and hasattr(user_obj, 'profile') and user_obj.profile.avatar and not user_obj.profile.prefer_initials:
            avatar_url = user_obj.profile.avatar.url
            
        feedback_list.append({
            'user': user_obj.get_full_name() if user_obj else "Unknown",
            'avatar_url': avatar_url,
            'ticket_id': s.ticket.id,
            'ticket': f"#{s.ticket.id}: {s.ticket.title}",
            'rating': s.rating,
            'comment': s.comment,
            'date': s.submitted_at
        })

    return render(request, 'service_desk/csat_report.html', {
        'feedback': feedback_list,
        'current_range': date_range,
        'technician': technician
    })

# ============================================================================
# TICKET QUICK VIEW (FOR KANBAN DRAWER)
# ============================================================================

@login_required
@user_passes_test(lambda u: u.is_staff)
def ticket_quick_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    comments = ticket.comments.all().order_by('-created_at')
    
    from inventory.models import HardwareAsset
    user_assets = HardwareAsset.objects.filter(assigned_to=ticket.submitter)
    
    primary_asset = user_assets.filter(category__name__in=['Laptops', 'Desktops']).first()

    return render(request, 'service_desk/partials/ticket_drawer.html', {
        'ticket': ticket,
        'comments': comments,
        'asset': primary_asset
    })

# ============================================================================
# AGENT TICKET CREATION (POWER FORM)
# ============================================================================

@login_required
@user_passes_test(lambda u: u.is_staff)
def agent_create_ticket(request):
    if request.method == 'POST':
        master_form = AgentTicketForm(request.POST)
        specific_form = None
        service_type = None
        
        if master_form.is_valid():
            service_type = master_form.cleaned_data['type']
            
            if service_type and service_type.form_class_name:
                try:
                    form_class = getattr(sys.modules[__name__], service_type.form_class_name)
                    specific_form = form_class(request.POST, request.FILES)
                except AttributeError:
                    specific_form = GeneralQuestionForm(request.POST, request.FILES)
            else:
                specific_form = GeneralQuestionForm(request.POST, request.FILES)

            if specific_form.is_valid():
                ticket = master_form.save(commit=False)
                
                ticket.submitter = master_form.cleaned_data['contact']
                # UPDATED: Use the form field, defaulting to None if empty
                ticket.technician = master_form.cleaned_data.get('technician')
                
                profile = getattr(ticket.submitter, 'profile', None)
                if profile:
                    ticket.contact_phone = profile.phone_office
                    ticket.contact_email = ticket.submitter.email
                    ticket.department = profile.department
                    ticket.location = profile.location

                specific_data = specific_form.cleaned_data
                for field, value in specific_data.items():
                    if hasattr(ticket, field):
                        setattr(ticket, field, value)
                
                if 'title' not in specific_data:
                    ticket.title = f"{service_type.name} - {specific_data.get('summary', 'No Summary')}"
                
                ticket.save()
                messages.success(request, f"Ticket #{ticket.id} created successfully.")
                return redirect('workspace')
    
    else:
        master_form = AgentTicketForm()

    return render(request, 'service_desk/agent_create_ticket.html', {
        'master_form': master_form
    })

# --- HTMX HELPER ENDPOINTS ---

@login_required
def hx_load_types(request):
    board_id = request.GET.get('board')
    types = ServiceType.objects.filter(boards__id=board_id, is_active=True).order_by('name')
    return render(request, 'service_desk/partials/options_list.html', {'options': types})

@login_required
def hx_load_subtypes(request):
    type_id = request.GET.get('type')
    subtypes = ServiceSubtype.objects.filter(parent_types__id=type_id, is_active=True).order_by('name')
    return render(request, 'service_desk/partials/options_list.html', {'options': subtypes})

@login_required
def hx_load_items(request):
    subtype_id = request.GET.get('subtype')
    items = ServiceItem.objects.filter(parent_subtypes__id=subtype_id, is_active=True).order_by('name')
    return render(request, 'service_desk/partials/options_list.html', {'options': items})

@login_required
def hx_load_ticket_form(request):
    type_id = request.GET.get('type')
    if not type_id:
        return HttpResponse("") 

    service_type = get_object_or_404(ServiceType, id=type_id)
    form_class_name = service_type.form_class_name or 'GeneralQuestionForm'
    
    try:
        form_class = getattr(sys.modules[__name__], form_class_name)
        form = form_class()
        return render(request, 'service_desk/forms/agent_form_partial.html', {'form': form})
        
    except AttributeError:
        return HttpResponse(f"<p class='text-red-500'>Error: Form '{form_class_name}' not found.</p>")

@login_required
def hx_get_contact_info(request):
    user_id = request.GET.get('contact')
    user = get_object_or_404(User, pk=user_id)
    profile = user.profile
    
    return render(request, 'service_desk/partials/contact_info_inputs.html', {
        'user': user,
        'profile': profile
    })

@login_required
def hx_search_users(request):
    query = request.GET.get('q', '').strip()
    target = request.GET.get('target', 'contact')
    variant = request.GET.get('variant', 'full') # Capture variant (default to 'full')
    
    users = User.objects.filter(is_active=True).select_related('profile')
    
    if target == 'technician' or target == 'collaborators':
        users = users.filter(groups__name='Service Desk')

    if query:
        users = users.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(username__icontains=query) |
            Q(email__icontains=query)
        ).distinct()[:25]
    else:
        users = users.order_by('first_name')[:25]
        
    return render(request, 'service_desk/partials/user_search_results.html', {
        'users': users,
        'target': target,
        'variant': variant # Pass variant to template
    })

# --- Omni-Search Engine ---
def omni_search(request):
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return HttpResponse('') 

    tickets = Ticket.objects.filter(
        Q(id__icontains=query) | 
        Q(title__icontains=query) | 
        Q(description__icontains=query)
    ).distinct()[:5]

    assets = HardwareAsset.objects.filter(
        Q(asset_tag__icontains=query) | 
        Q(serial_number__icontains=query) |
        Q(assigned_to__username__icontains=query) |
        Q(assigned_to__first_name__icontains=query) |
        Q(assigned_to__last_name__icontains=query)
    ).distinct()[:5]

    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    ).distinct()[:5]

    kb_articles = Article.objects.filter(
        Q(title__icontains=query) | 
        Q(problem__icontains=query) | 
        Q(solution__icontains=query)
    ).distinct()[:5]

    context = {
        'query': query,
        'tickets': tickets,
        'assets': assets,
        'users': users,
        'kb_articles': kb_articles,
        'total_count': tickets.count() + assets.count() + users.count() + kb_articles.count()
    }

    return render(request, 'service_desk/partials/omni_search_results.html', context)

# --- Ticket Registry (The "Power" Search) ---
@login_required
def ticket_registry(request):
    tickets = Ticket.objects.all().order_by('-created_at')

    query = request.GET.get('q', '')
    if query:
        tickets = tickets.filter(
            Q(id__icontains=query) |
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(technician__first_name__icontains=query) |
            Q(technician__last_name__icontains=query) |
            Q(technician__username__icontains=query) |
            Q(submitter__first_name__icontains=query) |
            Q(submitter__last_name__icontains=query) |
            Q(submitter__username__icontains=query)
        )

    status = request.GET.get('status', '')
    if status:
        tickets = tickets.filter(status=status)

    priority = request.GET.get('priority', '')
    if priority:
        tickets = tickets.filter(priority=priority)

    tech_id = request.GET.get('tech', '')
    if tech_id:
        tickets = tickets.filter(technician_id=tech_id)

    submitter_id = request.GET.get('submitter', '')
    if submitter_id:
        tickets = tickets.filter(submitter_id=submitter_id)

    board_id = request.GET.get('board', '')
    if board_id:
        tickets = tickets.filter(board_id=board_id)

    paginator = Paginator(tickets, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tickets': page_obj,
        'query': query,
        'technicians': User.objects.filter(is_staff=True).order_by('first_name'),
        'boards': ServiceBoard.objects.all(),
        'statuses': ['New', 'In Progress', 'On Hold', 'Waiting on User', 'Resolved', 'Closed', 'Reopened'], 
        'priorities': ['P1', 'P2', 'P3', 'P4'],
    }

    if request.headers.get('HX-Request'):
        return render(request, 'service_desk/partials/registry_table_rows.html', context)

    return render(request, 'service_desk/ticket_registry.html', context)

# --- Asset Detail View (THE FIX) ---
def asset_detail(request, asset_id):
    asset = get_object_or_404(HardwareAsset, id=asset_id)
    
    # Find tickets related to this asset (matching by Asset Tag)
    related_tickets = Ticket.objects.filter(
        Q(description__icontains=asset.asset_tag) | 
        Q(title__icontains=asset.asset_tag)
    ).order_by('-created_at')

    return render(request, 'inventory/asset_detail.html', {
        'asset': asset,
        'related_tickets': related_tickets
    })

# --- User Dossier (Read-Only View) (THE FIX) ---
@login_required
def user_dossier(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    
    # 1. Fetch Assets assigned to this user
    assigned_assets = HardwareAsset.objects.filter(assigned_to=target_user)
    
    # 2. Fetch recent tickets submitted by this user
    recent_tickets = Ticket.objects.filter(submitter=target_user).order_by('-created_at')[:5]

    # 3. Check if target is a technician (for the "Performance Metrics" button)
    is_technician = target_user.groups.filter(name='Service Desk').exists() or target_user.is_staff
    
    return render(request, 'service_desk/user_dossier.html', {
        'target_user': target_user,
        'assets': assigned_assets,
        'tickets': recent_tickets,
        'is_technician': is_technician
    })

@login_required
def hx_search_users(request):
    """
    HTMX Endpoint: Live user search for Agent Ticket Form & Details View.
    """
    query = request.GET.get('q', '').strip()
    target = request.GET.get('target', 'contact') # 'contact', 'technician', or 'collaborators'
    
    # Base query with optimization for profiles (avatars)
    users = User.objects.filter(is_active=True).select_related('profile')
    
    # RESTRICTION: If searching for Assignee OR Collaborators, only show Service Desk members
    if target == 'technician' or target == 'collaborators':
        users = users.filter(groups__name='Service Desk')

    if query:
        users = users.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(username__icontains=query) |
            Q(email__icontains=query)
        ).distinct()[:25]
    else:
        # Default: Top 25 alphabetical
        users = users.order_by('first_name')[:25]
        
    return render(request, 'service_desk/partials/user_search_results.html', {
        'users': users,
        'target': target
    })
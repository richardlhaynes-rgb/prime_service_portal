from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import (
    ApplicationIssueForm, EmailMailboxForm, HardwareIssueForm, PrinterScannerForm,
    SoftwareInstallForm, GeneralQuestionForm, VPResetForm, VPPermissionsForm,
    TicketReplyForm
)
from .models import Ticket, Comment
from services import ticket_service

# --- USER DASHBOARD ---
def dashboard(request):
    """
    Main Dashboard: Shows user's tickets with sorting capability.
    """
    # Get sort parameter from query string
    sort_by = request.GET.get('sort', '-created_at')
    
    # Fetch tickets using the service layer
    tickets = ticket_service.get_all_tickets(user=request.user)
    
    # Sort tickets based on parameter
    if sort_by.startswith('-'):
        reverse = True
        sort_field = sort_by[1:]
    else:
        reverse = False
        sort_field = sort_by
    
    # Sort the list
    if sort_field in ['id', 'title', 'ticket_type', 'status', 'priority', 'created_at']:
        tickets = sorted(tickets, key=lambda x: x.get(sort_field, ''), reverse=reverse)
    
    # Calculate stats
    stats = ticket_service.get_ticket_stats(tickets)
    
    return render(request, 'service_desk/dashboard.html', {
        'tickets': tickets,
        'stats': stats,
        'current_sort': sort_by
    })

# --- SERVICE CATALOG ---
def service_catalog(request):
    """
    Displays the 8-card Service Catalog grid.
    """
    return render(request, 'service_catalog.html')

# --- TICKET SUBMISSION FORMS ---
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

def report_email_issue(request):
    if request.method == 'POST':
        form = EmailMailboxForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            title = f'[Portal] Email Request: {data["request_type"]}'
            desc = f'USER REPORT:\n-----------------\nType: {data["request_type"]}\nMailbox: {data["mailbox_name"] or "N/A"}\nSummary: {data["summary"]}\n\nDETAILS:\n{data["description"]}'
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

def report_hardware_issue(request):
    if request.method == 'POST':
        form = HardwareIssueForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            title = f'[Portal] Hardware: {data["hardware_type"]} - {data["summary"]}'
            desc = f'USER REPORT:\n-----------------\nHardware: {data["hardware_type"]}\nAsset: {data["asset_tag"] or "Unknown"}\nLocation: {data["location"] or "N/A"}\n\nDETAILS:\n{data["description"]}'
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

def report_printer_issue(request):
    if request.method == 'POST':
        form = PrinterScannerForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            title = f'[Portal] Printer Issue at {data["printer_location"]}'
            desc = f'USER REPORT:\n-----------------\nLocation: {data["printer_location"]}\nComputer: {data["computer_name"] or "N/A"}\n\nDETAILS:\n{data["description"]}'
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

def report_software_install(request):
    if request.method == 'POST':
        form = SoftwareInstallForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user_display = 'Myself'
            if data['request_for'] == 'Another User':
                user_display = f'Another User ({data["target_user"]})'
            title = f'[Portal] Software Request: {data["software_name"]}'
            desc = f'USER REPORT:\n-----------------\nSoftware: {data["software_name"]}\nVersion: {data["version_needed"] or "Latest"}\nRequest For: {user_display}\nComputer: {data["computer_name"]}\n\nJUSTIFICATION:\n{data["justification"]}\n\nLICENSE:\n{data["license_info"] or "None"}'
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
def ticket_detail(request, ticket_id):
    """
    Displays a single ticket with comments and allows user to reply.
    Includes Demo Mode detection.
    """
    # Check if we're in Demo Mode
    is_demo_mode = ticket_service.USE_MOCK_DATA
    
    if is_demo_mode:
        # Demo Mode: Fetch from service layer (JSON)
        ticket = ticket_service.get_ticket_by_id(ticket_id)
        if not ticket:
            messages.error(request, "Ticket not found.")
            return redirect('dashboard')
        
        # Mock comments (empty for demo)
        comments = []
        
        # Initialize form with empty data
        form = TicketReplyForm()
        
        # Handle form submission (but don't save in Demo Mode)
        if request.method == 'POST':
            form = TicketReplyForm(request.POST)
            if form.is_valid():
                messages.warning(request, "Demo Mode: Your changes were not saved to the database.")
                return redirect('ticket_detail', ticket_id=ticket_id)
    else:
        # Live Mode: Fetch from database
        ticket = get_object_or_404(Ticket, id=ticket_id)
        comments = ticket.comments.all()
        
        # Handle form submission
        if request.method == 'POST':
            form = TicketReplyForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                
                # Add comment if provided
                if data['comment']:
                    Comment.objects.create(
                        ticket=ticket,
                        author=request.user,
                        text=data['comment']
                    )
                    messages.success(request, "Your comment has been added.")
                
                # Update priority if changed
                if data['priority']:
                    ticket.priority = data['priority']
                    ticket.save()
                    messages.success(request, f"Priority updated to {ticket.get_priority_display()}.")
                
                # Close ticket if requested
                if data['close_ticket']:
                    ticket.status = Ticket.Status.CLOSED
                    ticket.save()
                    messages.success(request, "Ticket has been closed.")
                
                return redirect('ticket_detail', ticket_id=ticket.id)
        else:
            form = TicketReplyForm(initial={'priority': ticket.priority})
    
    return render(request, 'service_desk/ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'form': form,
        'is_demo_mode': is_demo_mode
    })

# --- TICKET SURVEY (CSAT Feedback Portal) ---
def ticket_survey(request, ticket_id):
    """
    Public-facing survey form for customer satisfaction (CSAT) feedback.
    """
    # Check if we're in Demo Mode
    is_demo_mode = ticket_service.USE_MOCK_DATA
    
    if is_demo_mode:
        # Demo Mode: Mock ticket data
        ticket = ticket_service.get_ticket_by_id(ticket_id)
        if not ticket:
            messages.error(request, "Ticket not found.")
            return redirect('dashboard')
    else:
        # Live Mode: Fetch from database
        ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comments = request.POST.get('comments')
        
        if is_demo_mode:
            # Demo Mode: Display message but don't save
            messages.success(request, f"Demo Mode: Feedback received (Rating: {rating}/5). Data not saved.")
        else:
            # Live Mode: Save to database (future implementation)
            messages.success(request, f"Thank you for your feedback! Your rating: {rating}/5")
        
        return redirect('dashboard')
    
    return render(request, 'service_desk/ticket_survey.html', {
        'ticket': ticket,
        'is_demo_mode': is_demo_mode
    })

# --- MANAGER ANALYTICS DASHBOARD ---
@login_required
def manager_dashboard(request):
    """
    Manager Dashboard: Analytics, SLA breaches, team roster.
    """
    # Check if user has permission
    if not request.user.is_superuser:
        messages.error(request, "Access Denied: Manager-level permissions required.")
        return redirect('dashboard')
    
    # Get date range from query parameters
    date_range = request.GET.get('range', '7d')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    # Fetch analytics data
    analytics = ticket_service.get_dashboard_stats(
        date_range=date_range,
        start_date=start_date,
        end_date=end_date
    )
    
    return render(request, 'service_desk/manager_dashboard.html', {
        'stats': analytics,
        'analytics': analytics,
        'current_range': date_range
    })

# --- CSAT REPORT ---
@login_required
def csat_report(request):
    """
    CSAT Report: Displays customer satisfaction ratings and feedback.
    """
    # Check if user has permission
    if not request.user.is_superuser:
        messages.error(request, "Access Denied: Manager-level permissions required.")
        return redirect('dashboard')
    
    return render(request, 'service_desk/csat_report.html', {
        'feedback_data': []  # Future: Populate from database
    })

# --- ADMIN SETTINGS (System Health Configuration) ---
@login_required
def admin_settings(request):
    """
    Admin Settings: Configure System Health announcements and vendor status.
    """
    # Check if user has permission
    if not request.user.is_superuser:
        messages.error(request, "Access Denied: Manager-level permissions required.")
        return redirect('dashboard')
    
    # Load current system health data
    current_health = ticket_service.get_dashboard_stats()['system_health']
    
    if request.method == 'POST':
        # Parse form data
        announcement_title = request.POST.get('announcement_title')
        announcement_message = request.POST.get('announcement_message')
        announcement_type = request.POST.get('announcement_type')
        
        # Build vendor status list
        vendor_status = []
        vendor_names = request.POST.getlist('vendor_name[]')
        vendor_statuses = request.POST.getlist('vendor_status[]')
        
        for name, status in zip(vendor_names, vendor_statuses):
            if name:  # Only add non-empty entries
                vendor_status.append({'name': name, 'status': status})
        
        # Save to JSON file
        new_health_data = {
            'announcement': {
                'title': announcement_title,
                'message': announcement_message,
                'type': announcement_type,
                'date': 'Today'
            },
            'vendor_status': vendor_status
        }
        
        ticket_service.update_system_health(new_health_data)
        messages.success(request, "System Health settings updated successfully!")
        return redirect('admin_settings')
    
    return render(request, 'service_desk/admin_settings.html', {
        'current_health': current_health
    })

# --- TECHNICIAN PROFILE ---
@login_required
def technician_profile(request, name):
    """
    Displays detailed profile for a specific technician.
    
    Args:
        name: URL-safe ID of the technician (e.g., 'richard_haynes')
    """
    # Check if user has permission
    if not request.user.is_superuser:
        messages.error(request, "Access Denied: Manager-level permissions required.")
        return redirect('dashboard')
    
    # Fetch technician data using the service layer
    tech_data = ticket_service.get_technician_details(name)
    
    if not tech_data:
        messages.error(request, f"Technician profile not found: {name}")
        return redirect('manager_dashboard')
    
    return render(request, 'service_desk/technician_profile.html', {
        'technician': tech_data
    })
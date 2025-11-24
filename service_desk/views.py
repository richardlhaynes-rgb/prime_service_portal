from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from .forms import (
    ApplicationIssueForm, EmailMailboxForm, HardwareIssueForm, PrinterScannerForm,
    SoftwareInstallForm, GeneralQuestionForm, VPResetForm, VPPermissionsForm, TicketReplyForm
)
from .models import Ticket, Comment

# --- IMPORT THE SERVICE LAYER ---
from services import ticket_service

# --- 1. THE DASHBOARD ---
def dashboard(request):
    # Use the Service Layer instead of direct database query
    tickets = ticket_service.get_all_tickets(user=request.user)
    stats = ticket_service.get_ticket_stats(tickets)
    
    # Sorting logic (only applies if NOT using mock data)
    sort_by = request.GET.get('sort', '-created_at')
    
    if not ticket_service.USE_MOCK_DATA:
        # Apply Django ORM sorting
        priority_order = Case(
            When(priority='Critical', then=Value(1)),
            When(priority='High', then=Value(2)),
            When(priority='Medium', then=Value(3)),
            When(priority='Low', then=Value(4)),
            output_field=IntegerField(),
        )
        
        if sort_by == 'priority':
            tickets = tickets.alias(priority_rank=priority_order).order_by('priority_rank')
        elif sort_by == '-priority':
            tickets = tickets.alias(priority_rank=priority_order).order_by('-priority_rank')
        else:
            valid_sorts = ['id', '-id', 'title', '-title', 'ticket_type', '-ticket_type', 'status', '-status', 'created_at', '-created_at']
            if sort_by in valid_sorts:
                tickets = tickets.order_by(sort_by)
    else:
        # Mock data: Apply basic sorting to the list of dicts
        if sort_by == 'title':
            tickets = sorted(tickets, key=lambda x: x['title'])
        elif sort_by == '-title':
            tickets = sorted(tickets, key=lambda x: x['title'], reverse=True)
        elif sort_by == 'status':
            tickets = sorted(tickets, key=lambda x: x['status'])
        elif sort_by == '-status':
            tickets = sorted(tickets, key=lambda x: x['status'], reverse=True)
        # Default: sort by created_at (newest first)
        else:
            tickets = sorted(tickets, key=lambda x: x.get('created_at', ''), reverse=True)

    context = {
        'tickets': tickets,
        'total_tickets': stats['total'],
        'open_tickets': stats['open'],
        'resolved_tickets': stats['resolved'],
        'current_sort': sort_by,
    }
    return render(request, 'dashboard.html', context)

# --- 2. TICKET DETAIL & REPLY ---
def ticket_detail(request, pk):
    ticket = ticket_service.get_ticket_by_id(pk)
    
    if not ticket:
        messages.error(request, "Ticket not found.")
        return redirect('dashboard')
    
    # --- ALWAYS CREATE THE FORM (for visual demonstration) ---
    comments = []
    form = None
    is_demo_mode = ticket_service.USE_MOCK_DATA
    
    if is_demo_mode:
        # Demo Mode: Show warning but still display the form
        messages.warning(request, "⚠️ DEMO MODE: This form is for demonstration only. Changes will not be saved.")
        # Create an empty form with the ticket's current priority (from JSON)
        form = TicketReplyForm(initial={'priority': ticket.get('priority', 'Medium')})
        comments = []  # No comments in demo mode
    else:
        # Live Mode: Full functionality
        ticket = get_object_or_404(Ticket, pk=pk)
        comments = ticket.comments.all()
        
        if request.method == 'POST':
            form = TicketReplyForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data.get('comment')
                if text:
                    Comment.objects.create(ticket=ticket, author=request.user, text=text)
                    messages.success(request, "Comment added.")
                
                new_priority = form.cleaned_data.get('priority')
                if new_priority and new_priority != ticket.priority:
                    ticket.priority = new_priority
                    ticket.save()
                    messages.info(request, "Priority updated.")

                if form.cleaned_data.get('close_ticket'):
                    ticket.status = Ticket.Status.CLOSED
                    ticket.save()
                    messages.success(request, "Ticket closed.")
                    return redirect('dashboard')

                return redirect('ticket_detail', pk=ticket.id)
        else:
            form = TicketReplyForm(initial={'priority': ticket.priority})
    
    return render(request, 'service_desk/ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'form': form,
        'is_demo_mode': is_demo_mode
    })

# --- 3. THE CATALOG ---
def service_catalog(request):
    return render(request, 'service_catalog.html')

# --- 4. REPORTING FORMS ---
# (No changes needed - these create NEW tickets in the database)

def report_application_issue(request):
    if request.method == 'POST':
        form = ApplicationIssueForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            app = data['application_name']
            if app == 'Other' and data['other_application']: app = f"Other ({data['other_application']})"
            title = f"[Portal] App Issue: {app} - {data['summary']}"
            desc = f"USER REPORT:\n-----------------\nApp: {app}\nComputer: {data['computer_name'] or 'Primary'}\n\nDETAILS:\n{data['description']}"
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.APPLICATION, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f"Ticket Submitted: {title}")
            return redirect('dashboard')
    else:
        form = ApplicationIssueForm()
    return render(request, 'service_desk/forms/application_issue.html', {'form': form})

def report_email_issue(request):
    if request.method == 'POST':
        form = EmailMailboxForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            title = f"[Portal] Email: {data['request_type']} - {data['summary']}"
            desc = f"USER REPORT:\n-----------------\nType: {data['request_type']}\nTarget: {data['mailbox_name'] or 'N/A'}\n\nDETAILS:\n{data['description']}"
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.EMAIL, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f"Ticket Submitted: {title}")
            return redirect('dashboard')
    else:
        form = EmailMailboxForm()
    return render(request, 'service_desk/forms/email_issue.html', {'form': form})

def report_hardware_issue(request):
    if request.method == 'POST':
        form = HardwareIssueForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            title = f"[Portal] Hardware: {data['hardware_type']} - {data['summary']}"
            desc = f"USER REPORT:\n-----------------\nHardware: {data['hardware_type']}\nAsset: {data['asset_tag'] or 'Unknown'}\nLocation: {data['location'] or 'N/A'}\n\nDETAILS:\n{data['description']}"
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.HARDWARE, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f"Ticket Submitted: {title}")
            return redirect('dashboard')
    else:
        form = HardwareIssueForm()
    return render(request, 'service_desk/forms/hardware_issue.html', {'form': form})

def report_printer_issue(request):
    if request.method == 'POST':
        form = PrinterScannerForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            title = f"[Portal] Printer Issue at {data['printer_location']}"
            desc = f"USER REPORT:\n-----------------\nLocation: {data['printer_location']}\nComputer: {data['computer_name'] or 'N/A'}\n\nDETAILS:\n{data['description']}"
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.PRINTER, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f"Ticket Submitted: {title}")
            return redirect('dashboard')
    else:
        form = PrinterScannerForm()
    return render(request, 'service_desk/forms/printer_issue.html', {'form': form})

def report_software_install(request):
    if request.method == 'POST':
        form = SoftwareInstallForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user_display = "Myself"
            if data['request_for'] == 'Another User': user_display = f"Another User ({data['target_user']})"
            title = f"[Portal] Software Request: {data['software_name']}"
            desc = f"USER REPORT:\n-----------------\nSoftware: {data['software_name']}\nVersion: {data['version_needed'] or 'Latest'}\nRequest For: {user_display}\nComputer: {data['computer_name']}\n\nJUSTIFICATION:\n{data['justification']}\n\nLICENSE INFO:\n{data['license_info'] or 'None provided'}"
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.SOFTWARE, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f"Ticket Submitted: {title}")
            return redirect('dashboard')
    else:
        form = SoftwareInstallForm()
    return render(request, 'service_desk/forms/software_install.html', {'form': form})

def report_general_question(request):
    if request.method == 'POST':
        form = GeneralQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            title = f"[Portal] General Question: {data['summary']}"
            Ticket.objects.create(title=title, description=data['description'], ticket_type=Ticket.TicketType.GENERAL, submitter=request.user, priority=Ticket.Priority.P4, status=Ticket.Status.NEW)
            messages.success(request, f"Ticket Submitted: {title}")
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
            title = f"[Portal] VP Password Reset: {target_user}"
            desc = f"USER REPORT:\n-----------------\nName: {data['your_name']}\nDeltek Username: {target_user}\n\nDETAILS:\n{data['summary']}"
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.VP_RESET, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f"Ticket Submitted: {title}")
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
                req_type = f"Other ({data['other_type']})"
            title = f"[Portal] VP Permissions: {req_type}"
            desc = f"USER REPORT:\n-----------------\nRequest Type: {req_type}\nProject: {data['affected_project'] or 'N/A'}\nUsers: {data['user_list'] or 'N/A'}\n\nDETAILS:\n{data['summary']}"
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.VP_PERM, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f"Ticket Submitted: {title}")
            return redirect('dashboard')
    else:
        form = VPPermissionsForm()
    return render(request, 'service_desk/forms/vp_permissions.html', {'form': form})
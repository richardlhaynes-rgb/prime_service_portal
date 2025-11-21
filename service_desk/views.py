from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import (
    ApplicationIssueForm, EmailMailboxForm, HardwareIssueForm, PrinterScannerForm,
    SoftwareInstallForm, GeneralQuestionForm, VPResetForm, VPPermissionsForm
)
from .models import Ticket

# --- 1. THE DASHBOARD (Homepage) ---
def dashboard(request):
    # Fetch tickets for the current user
    if request.user.is_authenticated:
        user_tickets = Ticket.objects.filter(submitter=request.user).order_by('-created_at')
    else:
        user_tickets = Ticket.objects.none()

    # Stats Calculation
    total = user_tickets.count()
    resolved = user_tickets.filter(status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]).count()
    open_count = total - resolved

    context = {
        'tickets': user_tickets,
        'total_tickets': total,
        'open_tickets': open_count,
        'resolved_tickets': resolved,
    }
    return render(request, 'dashboard.html', context)

# --- 2. THE CATALOG (Grid) ---
def service_catalog(request):
    return render(request, 'service_catalog.html')


# --- 3. REPORTING FORMS ---

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
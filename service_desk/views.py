from django.shortcuts import render, redirect
from django.contrib import messages
# from django.contrib.auth.decorators import login_required
from .forms import ApplicationIssueForm, EmailMailboxForm, HardwareIssueForm, PrinterScannerForm
from .models import Ticket

# --- 1. Application Issue ---
def report_application_issue(request):
    if request.method == 'POST':
        form = ApplicationIssueForm(request.POST, request.FILES)
        if form.is_valid():
            app_name = form.cleaned_data['application_name']
            other_app = form.cleaned_data['other_application']
            summary = form.cleaned_data['summary']
            computer = form.cleaned_data['computer_name']
            details = form.cleaned_data['description']
            app_display = app_name
            if app_name == 'Other' and other_app: app_display = f"Other ({other_app})"
            formatted_title = f"[Portal] App Issue: {app_display} - {summary}"
            formatted_description = f"USER REPORT:\n-----------------\nApp: {app_display}\nComputer: {computer or 'Primary'}\n\nDETAILS:\n{details}"
            Ticket.objects.create(title=formatted_title, description=formatted_description, ticket_type=Ticket.TicketType.APPLICATION, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f"Ticket Submitted: {formatted_title}")
            return redirect('home')
    else:
        form = ApplicationIssueForm()
    return render(request, 'service_desk/forms/application_issue.html', {'form': form})

# --- 2. Email Issue ---
def report_email_issue(request):
    if request.method == 'POST':
        form = EmailMailboxForm(request.POST)
        if form.is_valid():
            req_type = form.cleaned_data['request_type']
            mailbox = form.cleaned_data['mailbox_name']
            summary = form.cleaned_data['summary']
            details = form.cleaned_data['description']
            formatted_title = f"[Portal] Email: {req_type} - {summary}"
            formatted_description = f"USER REPORT:\n-----------------\nType: {req_type}\nTarget: {mailbox or 'N/A'}\n\nDETAILS:\n{details}"
            Ticket.objects.create(title=formatted_title, description=formatted_description, ticket_type=Ticket.TicketType.EMAIL, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f"Ticket Submitted: {formatted_title}")
            return redirect('home')
    else:
        form = EmailMailboxForm()
    return render(request, 'service_desk/forms/email_issue.html', {'form': form})

# --- 3. Hardware Issue ---
def report_hardware_issue(request):
    if request.method == 'POST':
        form = HardwareIssueForm(request.POST, request.FILES)
        if form.is_valid():
            hw_type = form.cleaned_data['hardware_type']
            asset = form.cleaned_data['asset_tag']
            location = form.cleaned_data['location']
            summary = form.cleaned_data['summary']
            details = form.cleaned_data['description']
            formatted_title = f"[Portal] Hardware: {hw_type} - {summary}"
            formatted_description = f"USER REPORT:\n-----------------\nHardware Type: {hw_type}\nAsset Tag: {asset or 'Unknown'}\nLocation: {location or 'N/A'}\n\nDETAILS:\n{details}"
            Ticket.objects.create(title=formatted_title, description=formatted_description, ticket_type=Ticket.TicketType.HARDWARE, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f"Ticket Submitted: {formatted_title}")
            return redirect('home')
    else:
        form = HardwareIssueForm()
    return render(request, 'service_desk/forms/hardware_issue.html', {'form': form})

# --- 4. Printer/Scanner Issue (New) ---
def report_printer_issue(request):
    if request.method == 'POST':
        form = PrinterScannerForm(request.POST)
        if form.is_valid():
            location = form.cleaned_data['printer_location']
            details = form.cleaned_data['description']
            computer = form.cleaned_data['computer_name']

            # Constructing Title: [Portal] Printer Issue at {Location}
            formatted_title = f"[Portal] Printer Issue at {location}"
            
            formatted_description = f"""
            USER REPORT:
            ------------------------------------------------
            Location: {location}
            Affected Computer: {computer or 'N/A'}
            
            DETAILS:
            {details}
            """

            Ticket.objects.create(
                title=formatted_title,
                description=formatted_description,
                ticket_type=Ticket.TicketType.PRINTER,
                submitter=request.user,
                priority=Ticket.Priority.P3,
                status=Ticket.Status.NEW
            )
            messages.success(request, f"Ticket Submitted: {formatted_title}")
            return redirect('home')
    else:
        form = PrinterScannerForm()
    return render(request, 'service_desk/forms/printer_issue.html', {'form': form})
# --- PRIME Service Portal Update Script ---
# Run this from C:\Projects\prime_service_portal

$ErrorActionPreference = "Stop"
Write-Host "Starting Code Injection..." -ForegroundColor Cyan

# --- 1. UPDATE FORMS.PY ---
$formsContent = @"
from django import forms

# --- Shared Styling Class ---
INPUT_STYLE = 'w-full p-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-prime-orange focus:border-transparent'

# --- 1. Application Issue Form ---
class ApplicationIssueForm(forms.Form):
    APP_CHOICES = [
        ('', 'Select an Application...'),
        ('AutoCAD', 'AutoCAD'),
        ('Revit', 'Revit'),
        ('Civil 3D', 'Civil 3D'),
        ('MicroStation', 'MicroStation'),
        ('OpenRoads Designer', 'OpenRoads Designer'),
        ('ProjectWise Explorer Client', 'ProjectWise Explorer Client'),
        ('BIM 360 / Collaborate Pro', 'BIM 360 / Collaborate Pro'),
        ('ArcGIS Pro', 'ArcGIS Pro'),
        ('Acrobat Pro', 'Acrobat Pro'),
        ('Photoshop', 'Photoshop'),
        ('Microsoft Teams', 'Microsoft Teams'),
        ('Outlook', 'Outlook'),
        ('Excel', 'Excel'),
        ('Google Chrome', 'Google Chrome'),
        ('Windows OS', '(Windows / Operating System)'),
        ('Other', 'Other'),
    ]
    application_name = forms.ChoiceField(choices=APP_CHOICES, label="Application Name", widget=forms.Select(attrs={'class': INPUT_STYLE}))
    other_application = forms.CharField(required=False, label="Other Application", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "If 'Other' selected, please specify"}))
    computer_name = forms.CharField(required=False, label="Affected Computer (if not your own)", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "Leave blank if it's your primary computer"}))
    summary = forms.CharField(label="Summary of Problem", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "Ex: Revit crashing when opening file"}))
    description = forms.CharField(label="Detailed Description / Error Message", widget=forms.Textarea(attrs={'class': INPUT_STYLE + ' h-32', 'placeholder': "Describe steps taken, error text, when it began."}))
    screenshot = forms.FileField(required=False, label="Add Screenshot (Optional)", widget=forms.FileInput(attrs={'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-prime-orange file:text-white hover:file:bg-opacity-90'}))

# --- 2. Email & Mailbox Form ---
class EmailMailboxForm(forms.Form):
    TYPE_CHOICES = [
        ('', '-- Select Request Type --'),
        ('Shared Mailbox', 'Shared Mailbox Access/Issue'),
        ('Distribution List', 'Distribution List Change (Add/Remove)'),
        ('Storage', 'Mailbox Size/Storage Question'),
        ('Other', 'Other Email Issue'),
    ]
    request_type = forms.ChoiceField(choices=TYPE_CHOICES, label="Type of Request", widget=forms.Select(attrs={'class': INPUT_STYLE}))
    mailbox_name = forms.CharField(required=False, label="Mailbox or List Name (if applicable)", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "Ex: projects@primeeng.com, Marketing DL"}))
    summary = forms.CharField(label="Summary of Request", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "Ex: Add Jane Doe to Marketing DL"}))
    description = forms.CharField(label="Detailed Description / Users to Add/Remove", widget=forms.Textarea(attrs={'class': INPUT_STYLE + ' h-32', 'placeholder': "Names, emails, required permissions."}))

# --- 3. Hardware Issue Form ---
class HardwareIssueForm(forms.Form):
    HW_CHOICES = [
        ('', '-- Select Device Type --'),
        ('Laptop / Computer', 'Laptop / Computer'),
        ('Docking Station', 'Docking Station'),
        ('Monitor / Display', 'Monitor / Display'),
        ('Keyboard / Mouse', 'Keyboard / Mouse'),
        ('Headset / Microphone', 'Headset / Microphone'),
        ('Webcam / Camera', 'Webcam / Camera'),
        ('Printer / Plotter', 'Printer / Plotter'),
    ]
    hardware_type = forms.ChoiceField(choices=HW_CHOICES, label="Type of Hardware with Issue", widget=forms.Select(attrs={'class': INPUT_STYLE}))
    asset_tag = forms.CharField(required=False, label="Asset Tag or Device Name (if known)", widget=forms.TextInput(attrs={'class': INPUT_STYLE}))
    location = forms.CharField(required=False, label="Location of Shared Device (if applicable)", widget=forms.TextInput(attrs={'class': INPUT_STYLE}))
    summary = forms.CharField(label="Summary of Problem", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "e.g., Monitor won't turn on"}))
    description = forms.CharField(label="Detailed Description", widget=forms.Textarea(attrs={'class': INPUT_STYLE + ' h-32', 'placeholder': "Please provide details, including any errors."}))
    screenshot = forms.FileField(required=False, label="Add Screenshot or Photo (Optional)", widget=forms.FileInput(attrs={'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-prime-orange file:text-white hover:file:bg-opacity-90'}))

# --- 4. Printer & Scanner Form ---
class PrinterScannerForm(forms.Form):
    printer_location = forms.CharField(label="Printer/Scanner Location", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': 'Location (e.g., "Lexington 1st Floor")'}))
    description = forms.CharField(label="Summary of Problem", widget=forms.Textarea(attrs={'class': INPUT_STYLE + ' h-32', 'placeholder': "Please describe the problem in detail."}))
    computer_name = forms.CharField(required=False, label="Affected Computer (if not your own)", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "Leave blank if it's your primary computer"}))

# --- 5. Software Install Form ---
class SoftwareInstallForm(forms.Form):
    software_name = forms.CharField(label="Software Name", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "e.g., Adobe Photoshop, AutoCAD 2026"}))
    justification = forms.CharField(label="Business Justification / Project", widget=forms.Textarea(attrs={'class': INPUT_STYLE + ' h-24', 'placeholder': "e.g., Needed for Project XYZ graphics"}))
    REQUEST_FOR_CHOICES = [('Myself', 'Myself'), ('Another User', 'Another User')]
    request_for = forms.ChoiceField(label="Is this request for yourself or someone else?", choices=REQUEST_FOR_CHOICES, widget=forms.RadioSelect(attrs={'class': 'ml-2'}), initial='Myself')
    target_user = forms.CharField(required=False, label="User Requiring Software (if not yourself)", widget=forms.TextInput(attrs={'class': INPUT_STYLE}))
    computer_name = forms.CharField(label="Computer Name / Asset Tag", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "e.g., 001234 or DESKTOP-ABCDE"}))
    license_info = forms.CharField(required=False, label="License Information (if known)", widget=forms.Textarea(attrs={'class': INPUT_STYLE + ' h-24'}))

# --- 6. General Question Form ---
class GeneralQuestionForm(forms.Form):
    summary = forms.CharField(label="Subject", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "Briefly state your question or issue."}))
    description = forms.CharField(label="Your Question / Issue Details", widget=forms.Textarea(attrs={'class': INPUT_STYLE + ' h-32', 'placeholder': "Provide details about your question or problem."}))
    screenshot = forms.FileField(required=False, label="Add Screenshot (Optional)", widget=forms.FileInput(attrs={'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-prime-orange file:text-white hover:file:bg-opacity-90'}))

# --- 7. VP Reset Form ---
class VPResetForm(forms.Form):
    your_name = forms.CharField(label="Your Name", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "Please enter your full name"}))
    deltek_username = forms.CharField(required=False, label="Deltek Username (if different)", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "Leave blank if it's your email or full name"}))
    summary = forms.CharField(label="Summary of Problem", widget=forms.Textarea(attrs={'class': INPUT_STYLE + ' h-32', 'placeholder': 'e.g., "Forgot my password", "Password expired"'}))

# --- 8. VP Permissions Form ---
class VPPermissionsForm(forms.Form):
    TYPE_CHOICES = [('', '-- Select Request Type --'), ('Permission Change', 'Permission Change'), ('Project Update', 'Project Update'), ('Report an Error', 'Report an Error'), ('General Question', 'General Question'), ('Other', 'Other')]
    request_type = forms.ChoiceField(label="Request Type", choices=TYPE_CHOICES, widget=forms.Select(attrs={'class': INPUT_STYLE}))
    other_type = forms.CharField(required=False, label="If 'Other', please specify", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "If 'Other' selected, please specify"}))
    affected_project = forms.CharField(required=False, label="Affected Project (if any)", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "(Optional) e.g., 2025-123.00"}))
    user_list = forms.CharField(required=False, label="List of Users (if adding/removing)", widget=forms.Textarea(attrs={'class': INPUT_STYLE + ' h-24', 'placeholder': "(Optional) e.g., John Smith, Jane Doe"}))
    summary = forms.CharField(label="Summary of Problem or Request", widget=forms.Textarea(attrs={'class': INPUT_STYLE + ' h-32', 'placeholder': "Please add John Smith to project X"}))
"@
Set-Content -Path "service_desk/forms.py" -Value $formsContent -Encoding UTF8
Write-Host "forms.py Updated." -ForegroundColor Green

# --- 2. UPDATE VIEWS.PY ---
$viewsContent = @"
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import (
    ApplicationIssueForm, EmailMailboxForm, HardwareIssueForm, PrinterScannerForm,
    SoftwareInstallForm, GeneralQuestionForm, VPResetForm, VPPermissionsForm
)
from .models import Ticket

def report_application_issue(request):
    if request.method == 'POST':
        form = ApplicationIssueForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            app = data['application_name']
            if app == 'Other' and data['other_application']: app = f'Other ({data["other_application"]})'
            title = f'[Portal] App Issue: {app} - {data["summary"]}'
            desc = f'USER REPORT:\n-----------------\nApp: {app}\nComputer: {data["computer_name"] or "Primary"}\n\nDETAILS:\n{data["description"]}'
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.APPLICATION, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('home')
    else:
        form = ApplicationIssueForm()
    return render(request, 'service_desk/forms/application_issue.html', {'form': form})

def report_email_issue(request):
    if request.method == 'POST':
        form = EmailMailboxForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            title = f'[Portal] Email: {data["request_type"]} - {data["summary"]}'
            desc = f'USER REPORT:\n-----------------\nType: {data["request_type"]}\nTarget: {data["mailbox_name"] or "N/A"}\n\nDETAILS:\n{data["description"]}'
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.EMAIL, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('home')
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
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.HARDWARE, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('home')
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
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.PRINTER, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('home')
    else:
        form = PrinterScannerForm()
    return render(request, 'service_desk/forms/printer_issue.html', {'form': form})

def report_software_install(request):
    if request.method == 'POST':
        form = SoftwareInstallForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user_display = 'Myself'
            if data['request_for'] == 'Another User': user_display = f'Another User ({data["target_user"]})'
            title = f'[Portal] Software Request: {data["software_name"]}'
            desc = f'USER REPORT:\n-----------------\nSoftware: {data["software_name"]}\nVersion: {data["version_needed"] or "Latest"}\nRequest For: {user_display}\nComputer: {data["computer_name"]}\n\nJUSTIFICATION:\n{data["justification"]}\n\nLICENSE:\n{data["license_info"] or "None"}'
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.SOFTWARE, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('home')
    else:
        form = SoftwareInstallForm()
    return render(request, 'service_desk/forms/software_install.html', {'form': form})

def report_general_question(request):
    if request.method == 'POST':
        form = GeneralQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            title = f'[Portal] General Question: {data["summary"]}'
            Ticket.objects.create(title=title, description=data['description'], ticket_type=Ticket.TicketType.GENERAL, submitter=request.user, priority=Ticket.Priority.P4, status=Ticket.Status.NEW)
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('home')
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
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.VP_RESET, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('home')
    else:
        form = VPResetForm()
    return render(request, 'service_desk/forms/vp_reset.html', {'form': form})

def report_vp_permissions(request):
    if request.method == 'POST':
        form = VPPermissionsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            req_type = data['request_type']
            if req_type == 'Other' and data['other_type']: req_type = f'Other ({data["other_type"]})'
            title = f'[Portal] VP Permissions: {req_type}'
            desc = f'USER REPORT:\n-----------------\nRequest Type: {req_type}\nProject: {data["affected_project"] or "N/A"}\nUsers: {data["user_list"] or "N/A"}\n\nDETAILS:\n{data["summary"]}'
            Ticket.objects.create(title=title, description=desc, ticket_type=Ticket.TicketType.VP_PERM, submitter=request.user, priority=Ticket.Priority.P3, status=Ticket.Status.NEW)
            messages.success(request, f'Ticket Submitted: {title}')
            return redirect('home')
    else:
        form = VPPermissionsForm()
    return render(request, 'service_desk/forms/vp_permissions.html', {'form': form})
"@
Set-Content -Path "service_desk/views.py" -Value $viewsContent -Encoding UTF8
Write-Host "views.py Updated." -ForegroundColor Green

# --- 3. UPDATE URLS.PY ---
$urlsContent = @"
from django.urls import path
from . import views

urlpatterns = [
    path('report/application/', views.report_application_issue, name='report_app_issue'),
    path('report/email/', views.report_email_issue, name='report_email_issue'),
    path('report/hardware/', views.report_hardware_issue, name='report_hardware_issue'),
    path('report/printer/', views.report_printer_issue, name='report_printer_issue'),
    path('request/software/', views.report_software_install, name='report_software_install'),
    path('report/general/', views.report_general_question, name='report_general_question'),
    path('request/vp-reset/', views.report_vp_reset, name='report_vp_reset'),
    path('request/vp-permissions/', views.report_vp_permissions, name='report_vp_permissions'),
]
"@
Set-Content -Path "service_desk/urls.py" -Value $urlsContent -Encoding UTF8
Write-Host "urls.py Updated." -ForegroundColor Green

Write-Host "Script Complete. Restart your server!" -ForegroundColor Yellow
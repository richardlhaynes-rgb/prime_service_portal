from django import forms
from .models import (
    Ticket, Comment, GlobalSettings, UserProfile, 
    ServiceBoard, ServiceType, ServiceSubtype, ServiceItem
)
from knowledge_base.models import Article
from django.contrib.auth.forms import UserCreationForm, UserChangeForm  # Shared auth forms
from django.contrib.auth.models import User, Group  # User + Groups for checkbox list
from django.utils.safestring import mark_safe

INPUT_STYLE = 'w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-prime-orange focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400'

# Shared Tailwind widget helpers for user forms
USER_TEXT_WIDGET = forms.TextInput(attrs={
    'class': 'w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:text-white'
})
USER_EMAIL_WIDGET = forms.EmailInput(attrs={
    'class': 'w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:text-white'
})
USER_CHECKBOX_WIDGET = forms.CheckboxInput(attrs={
    'class': 'h-5 w-5 text-prime-orange border-gray-300 dark:border-gray-600 rounded focus:ring-prime-orange'
})
USER_GROUPS_WIDGET = forms.CheckboxSelectMultiple(attrs={
    'class': 'space-y-2'
})

# --- Custom Trix RichText Widget ---
class RichTextWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        # Trix uses a hidden input to sync data. We hide the actual django textarea.
        attrs['hidden'] = True 
        html = super().render(name, value, attrs=attrs)
        
        # We construct the Trix Editor tag and link it to the hidden input via ID
        final_attrs = self.build_attrs(attrs)
        input_id = final_attrs.get('id', f'id_{name}')
        
        trix_html = f'<trix-editor input="{input_id}" class="trix-content w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:text-white px-3 py-2"></trix-editor>'
        return mark_safe(html + trix_html)

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
    description = forms.CharField(
        label="Detailed Description / Error Message",
        widget=RichTextWidget()
    )
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
    description = forms.CharField(
        label="Detailed Description / Users to Add/Remove",
        widget=RichTextWidget()
    )

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
    description = forms.CharField(
        label="Detailed Description",
        widget=RichTextWidget()
    )
    screenshot = forms.FileField(required=False, label="Add Screenshot or Photo (Optional)", widget=forms.FileInput(attrs={'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-prime-orange file:text-white hover:file:bg-opacity-90'}))

# --- 4. Printer & Scanner Form ---
class PrinterScannerForm(forms.Form):
    printer_location = forms.CharField(label="Printer/Scanner Location", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': 'Location (e.g., "Lexington 1st Floor")'}))
    description = forms.CharField(
        label="Summary of Problem",
        widget=RichTextWidget()
    )
    computer_name = forms.CharField(required=False, label="Affected Computer (if not your own)", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "Leave blank if it's your primary computer"}))

# --- 5. Software Install Form ---
class SoftwareInstallForm(forms.Form):
    software_name = forms.CharField(label="Software Name", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "e.g., Adobe Photoshop, AutoCAD 2026"}))
    justification = forms.CharField(
        label="Business Justification / Project",
        widget=RichTextWidget()
    )
    REQUEST_FOR_CHOICES = [('Myself', 'Myself'), ('Another User', 'Another User')]
    request_for = forms.ChoiceField(label="Is this request for yourself or someone else?", choices=REQUEST_FOR_CHOICES, widget=forms.RadioSelect(attrs={'class': 'ml-2'}), initial='Myself')
    target_user = forms.CharField(required=False, label="User Requiring Software (if not yourself)", widget=forms.TextInput(attrs={'class': INPUT_STYLE}))
    computer_name = forms.CharField(label="Computer Name / Asset Tag", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "e.g., 001234 or DESKTOP-ABCDE"}))
    license_info = forms.CharField(required=False, label="License Information (if known)", widget=forms.Textarea(attrs={'class': INPUT_STYLE + ' h-24'}))

# --- 6. General Question Form ---
class GeneralQuestionForm(forms.Form):
    summary = forms.CharField(label="Subject", widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "Briefly state your question or issue."}))
    description = forms.CharField(
        label="Your Question / Issue Details",
        widget=RichTextWidget()
    )
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

# --- 9. Ticket Reply Form (Comments Only) ---
class TicketReplyForm(forms.Form):
    comment = forms.CharField(
        label="Add Comment / Reply",
        required=False,
        widget=RichTextWidget()
    )
    
    # Close Ticket Checkbox
    close_ticket = forms.BooleanField(
        required=False,
        label="Close this ticket?",
        widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-prime-orange border-gray-300 rounded focus:ring-prime-orange'})
    )
    
    # Allow updating Priority (but not Status)
    priority = forms.ChoiceField(
        label="Update Priority",
        choices=Ticket.Priority.choices,
        required=False,
        widget=forms.Select(attrs={'class': INPUT_STYLE})
    )

# --- 10. Knowledge Base Article Form (NEW) ---
class KBArticleForm(forms.ModelForm):
    """
    ModelForm for creating and editing Knowledge Base articles.
    """
    class Meta:
        model = Article
        fields = ['title', 'category', 'subcategory', 'problem', 'solution', 'internal_notes', 'status']
        
        # Define the standard styling for all inputs (Light & Dark Mode compatible)
        # bg-white dark:bg-gray-700 -> Adapts background
        # text-gray-900 dark:text-gray-200 -> Adapts text color
        INPUT_STYLE = 'block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-200 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50'

        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': 'Enter article title...'}),
            'category': forms.Select(attrs={'class': INPUT_STYLE}),
            'subcategory': forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': 'e.g., Adobe, Bluebeam, Outlook'}),
            'problem': RichTextWidget(),
            'solution': RichTextWidget(),
            'internal_notes': RichTextWidget(),
            'status': forms.Select(attrs={'class': INPUT_STYLE}),
        }

# --- 11. Global Settings Form (Admin Configuration) ---
class GlobalSettingsForm(forms.ModelForm):
    """
    ModelForm for editing global site configuration.
    Used by superusers in the admin settings interface.
    """
    
    class Meta:
        model = GlobalSettings
        fields = [
            'maintenance_mode',
            'use_mock_data',
            'kb_recommendation_logic',
            'support_phone',
            'support_email',
            'support_hours',
        ]
        
        # Apply Tailwind CSS styling to all form widgets
        widgets = {
            'maintenance_mode': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-prime-orange focus:ring-prime-orange border-gray-300 rounded'
            }),
            'use_mock_data': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-prime-orange focus:ring-prime-orange border-gray-300 rounded'
            }),
            'kb_recommendation_logic': forms.Select(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white'
            }),
            'support_phone': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': '859-977-9641'
            }),
            'support_email': forms.EmailInput(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'support@primeeng.com'
            }),
            'support_hours': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Mon-Fri, 8:00 AM - 5:00 PM EST'
            }),
        }
        
        # Custom labels and help text
        labels = {
            'maintenance_mode': 'Enable Maintenance Mode',
            'use_mock_data': 'Use Demo/Mock Data',
            'kb_recommendation_logic': 'KB Article Sorting Logic',
            'support_phone': 'Support Phone Number',
            'support_email': 'Support Email Address',
            'support_hours': 'Support Hours',
        }
        
        help_texts = {
            'maintenance_mode': 'When enabled, non-admin users will see a maintenance page',
            'use_mock_data': 'Toggle between live ConnectWise data and demo JSON data',
            'kb_recommendation_logic': 'How KB articles are sorted on the homepage',
            'support_phone': 'Primary contact number displayed to users',
            'support_email': 'Primary support email displayed to users',
            'support_hours': 'Business hours displayed to users',
        }

# --- 12. Custom User Creation Form ---
class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:text-white',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:text-white',
            'autocomplete': 'new-password'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_superuser',
            'is_active',
            'groups',
        )
        widgets = {
            'username': USER_TEXT_WIDGET,
            'first_name': USER_TEXT_WIDGET,
            'last_name': USER_TEXT_WIDGET,
            'email': USER_EMAIL_WIDGET,
            'is_staff': USER_CHECKBOX_WIDGET,
            'is_superuser': USER_CHECKBOX_WIDGET,
            'is_active': USER_CHECKBOX_WIDGET,
            'groups': USER_GROUPS_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure groups are loaded for checkbox list
        self.fields['groups'].queryset = Group.objects.all()


# --- 13. Custom User Change Form (Admin Replacement) ---
class CustomUserChangeForm(UserChangeForm):
    password = None  # Hide password hash display

    # --- UserProfile fields ---
    title = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:text-white',
            'placeholder': 'e.g., Project Manager, Senior Engineer'
        })
    )
    department = forms.ChoiceField(
        required=False,
        choices=UserProfile.Department.choices,
        widget=forms.Select(attrs={
            'class': 'w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:text-white'
        })
    )
    company = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:text-white',
            'placeholder': 'PRIME AE Group, Inc.'
        })
    )
    location = forms.ChoiceField(
        required=False,
        choices=UserProfile.Site.choices,
        widget=forms.Select(attrs={
            'class': 'w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:text-white'
        })
    )
    phone_office = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:text-white',
            'placeholder': '859-555-1234'
        })
    )
    phone_mobile = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:text-white',
            'placeholder': '859-555-5678'
        })
    )
    manager_name = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:text-white',
            'placeholder': 'Direct Supervisor Name'
        })
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-prime-orange focus:ring focus:ring-prime-orange focus:ring-opacity-50 dark:bg-gray-700 dark:text-white',
            'rows': 3,
            'placeholder': 'Brief bio or notes about this user...'
        })
    )
    prefer_initials = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-5 w-5 text-prime-orange border-gray-300 dark:border-gray-600 rounded focus:ring-prime-orange'
        })
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'hidden', 'id': 'file-upload'})
    )

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_superuser',
            'is_active',
            'groups',
        )
        widgets = {
            'username': USER_TEXT_WIDGET,
            'first_name': USER_TEXT_WIDGET,
            'last_name': USER_TEXT_WIDGET,
            'email': USER_EMAIL_WIDGET,
            'is_staff': USER_CHECKBOX_WIDGET,
            'is_superuser': USER_CHECKBOX_WIDGET,
            'is_active': USER_CHECKBOX_WIDGET,
            'groups': USER_GROUPS_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['groups'].queryset = Group.objects.all()
        # Pre-fill profile fields from UserProfile
        if self.instance.pk:
            try:
                profile = self.instance.profile
                self.initial['title'] = profile.title
                self.initial['department'] = profile.department
                self.initial['company'] = profile.company
                self.initial['location'] = profile.location
                self.initial['phone_office'] = profile.phone_office
                self.initial['phone_mobile'] = profile.phone_mobile
                self.initial['manager_name'] = profile.manager_name
                self.initial['bio'] = profile.bio
                self.initial['prefer_initials'] = profile.prefer_initials
                self.initial['avatar'] = profile.avatar if profile.avatar else None
            except Exception:
                pass

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.title = self.cleaned_data.get('title', '')
        profile.department = self.cleaned_data.get('department', UserProfile.Department.CORPORATE)
        profile.company = self.cleaned_data.get('company', '')
        profile.location = self.cleaned_data.get('location', UserProfile.Site.REMOTE)
        profile.phone_office = self.cleaned_data.get('phone_office', '')
        profile.phone_mobile = self.cleaned_data.get('phone_mobile', '')
        profile.manager_name = self.cleaned_data.get('manager_name', '')
        profile.bio = self.cleaned_data.get('bio', '')
        profile.prefer_initials = self.cleaned_data.get('prefer_initials', False)
        if self.cleaned_data.get('avatar'):
            profile.avatar = self.cleaned_data['avatar']
        profile.save()
        return user

# --- NEW: AGENT MASTER TICKET FORM ---
class AgentTicketForm(forms.ModelForm):
    """
    The 'Power Form' for technicians.
    Includes cascading Classification fields (Board -> Type -> Subtype -> Item).
    """
    # 1. Contact Info (Who is this for?)
    contact = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('username'),
        widget=forms.HiddenInput(), # Controlled by JS Combobox
        label="Contact / User"
    )
    
    # 2. Technician (Assignee)
    technician = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('first_name'),
        required=False,
        label="Assignee",
        widget=forms.HiddenInput() # Controlled by JS Combobox
    )

    # 3. Collaborators (Multiple Select)
    collaborators = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        label="Collaborators",
        widget=forms.MultipleHiddenInput() # Controlled by JS Multi-Chip UI
    )
    
    # 4. Classification Hierarchy
    board = forms.ModelChoiceField(
        queryset=ServiceBoard.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': INPUT_STYLE,
            'hx-get': '/service-desk/htmx/load-types/',
            'hx-target': '#id_type'
        })
    )
    
    type = forms.ModelChoiceField(
        queryset=ServiceType.objects.none(), 
        widget=forms.Select(attrs={
            'class': INPUT_STYLE,
            'hx-get': '/service-desk/htmx/load-subtypes/',
            'hx-target': '#id_subtype',
            'hx-include': '#id_type',
            'hx-swap': 'innerHTML',
            '_': "on change htmx.ajax('GET', '/service-desk/htmx/load-form/?type=' + this.value, '#dynamic-form-container')"
        })
    )
    
    subtype = forms.ModelChoiceField(
        queryset=ServiceSubtype.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': INPUT_STYLE,
            'hx-get': '/service-desk/htmx/load-items/',
            'hx-target': '#id_item'
        })
    )
    
    item = forms.ModelChoiceField(
        queryset=ServiceItem.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': INPUT_STYLE})
    )

    class Meta:
        model = Ticket
        # UPDATED: Added 'technician' and 'collaborators' to fields list
        fields = ['contact', 'technician', 'collaborators', 'board', 'type', 'subtype', 'item', 'status', 'priority', 'source']
        widgets = {
            'status': forms.Select(attrs={'class': INPUT_STYLE}),
            'priority': forms.Select(attrs={'class': INPUT_STYLE}),
            'source': forms.Select(attrs={'class': INPUT_STYLE}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'board' in self.data:
            try:
                board_id = int(self.data.get('board'))
                self.fields['type'].queryset = ServiceType.objects.filter(boards__id=board_id).order_by('name')
            except (ValueError, TypeError):
                pass
        
        if 'type' in self.data:
            try:
                type_id = int(self.data.get('type'))
                self.fields['subtype'].queryset = ServiceSubtype.objects.filter(parent_types__id=type_id).order_by('name')
            except (ValueError, TypeError):
                pass
                
        if 'subtype' in self.data:
            try:
                subtype_id = int(self.data.get('subtype'))
                self.fields['item'].queryset = ServiceItem.objects.filter(parent_subtypes__id=subtype_id).order_by('name')
            except (ValueError, TypeError):
                pass
from django import forms
from .models import Ticket, Comment, GlobalSettings, UserProfile
from knowledge_base.models import Article
from django.contrib.auth.forms import UserCreationForm, UserChangeForm  # Shared auth forms
from django.contrib.auth.models import User, Group  # User + Groups for checkbox list

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

# --- 9. Ticket Reply Form (Comments Only) ---
class TicketReplyForm(forms.Form):
    comment = forms.CharField(
        label="Add Comment / Reply",
        required=False,
        widget=forms.Textarea(attrs={'class': INPUT_STYLE + ' h-24', 'placeholder': 'Add a note, reply to the technician...'})
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
class KBArticleForm(forms.Form):
    """
    Form for creating and editing Knowledge Base articles.
    Used by Manager/Admin users only.
    """
    
    # Category Choices (from Article.Category model)
    CATEGORY_CHOICES = [
        ('', '-- Select Category --'),
        ('Business & Admin Software', 'Business & Admin Software'),
        ('Design Applications', 'Design Applications'),
        ('Hardware & Peripherals', 'Hardware & Peripherals'),
        ('Internal IT Processes', 'Internal IT Processes'),
        ('Networking & Connectivity', 'Networking & Connectivity'),
        ('Printing & Plotting', 'Printing & Plotting'),
        ('User Accounts & Security', 'User Accounts & Security'),
    ]
    
    # Common Subcategory Choices (expandable list)
    SUBCATEGORY_CHOICES = [
        ('', '-- Select Subcategory --'),
        # Design Applications
        ('Adobe Creative Suite (Photoshop, InDesign)', 'Adobe Creative Suite (Photoshop, InDesign)'),
        ('Autodesk (AutoCAD, Revit, Civil 3D)', 'Autodesk (AutoCAD, Revit, Civil 3D)'),
        ('Bluebeam Revu (PDF & Markup)', 'Bluebeam Revu (PDF & Markup)'),
        ('Licensing & Activation', 'Licensing & Activation'),
        ('Other Design Tools (e.g., Lumion, Enscape, V-Ray)', 'Other Design Tools (e.g., Lumion, Enscape, V-Ray)'),
        ('SketchUp', 'SketchUp'),
        # Business & Admin Software
        ('Deltek (Vision, Vantagepoint, etc.)', 'Deltek (Vision, Vantagepoint, etc.)'),
        ('Email & Outlook', 'Email & Outlook'),
        ('File Storage & Sharing', 'File Storage & Sharing'),
        ('Microsoft 365 (Office, Teams, OneDrive)', 'Microsoft 365 (Office, Teams, OneDrive)'),
        ('Web Browsers', 'Web Browsers'),
        # Hardware & Peripherals
        ('Conference Room AV', 'Conference Room AV'),
        ('Mobile Devices (iPhones, iPads)', 'Mobile Devices (iPhones, iPads)'),
        ('Monitors & Docking Stations', 'Monitors & Docking Stations'),
        ('Specialty Peripherals (3Dconnexion mouse, etc.)', 'Specialty Peripherals (3Dconnexion mouse, etc.)'),
        ('Workstations (Desktops, Laptops)', 'Workstations (Desktops, Laptops)'),
        # Internal IT Processes
        ('Backup & Recovery', 'Backup & Recovery'),
        ('New User Onboarding', 'New User Onboarding'),
        ('Server Maintenance', 'Server Maintenance'),
        ('User Offboarding', 'User Offboarding'),
        ('Vendor Contact List', 'Vendor Contact List'),
        # Networking & Connectivity
        ('Internet Outage (Office-specific)', 'Internet Outage (Office-specific)'),
        ('VPN / Remote Access', 'VPN / Remote Access'),
        ('VPN Connection Issues', 'VPN Connection Issues'),
        ('Wi-Fi', 'Wi-Fi'),
        ('Wired / Ethernet', 'Wired / Ethernet'),
        # Printing & Plotting
        ('Desktop Printers & Copiers', 'Desktop Printers & Copiers'),
        ('Large Format Plotters', 'Large Format Plotters'),
        ('Print Management Software', 'Print Management Software'),
        ('Scan to Email / Scan to Folder', 'Scan to Email / Scan to Folder'),
        # User Accounts & Security
        ('File & Folder Permissions', 'File & Folder Permissions'),
        ('MFA (Multi-Factor Authentication)', 'MFA (Multi-Factor Authentication)'),
        ('Password Resets', 'Password Resets'),
        ('Security & Phishing', 'Security & Phishing'),
        # Generic fallback
        ('General', 'General'),
    ]
    
    # Status Choices (from Article.Status model)
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending', 'Pending Approval'),
        ('Approved', 'Approved'),
    ]
    
    # Form Fields
    title = forms.CharField(
        label="Article Title",
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': INPUT_STYLE,
            'placeholder': 'e.g., "AutoCAD: How to Reset to Default Settings"'
        })
    )
    
    category = forms.ChoiceField(
        label="Category",
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': INPUT_STYLE})
    )
    
    subcategory = forms.ChoiceField(
        label="Subcategory",
        choices=SUBCATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': INPUT_STYLE})
    )
    
    problem = forms.CharField(
        label="Issue / Problem Description",
        widget=forms.Textarea(attrs={
            'class': INPUT_STYLE,
            'rows': 4,
            'placeholder': 'Describe the symptoms or error the user is experiencing...'
        })
    )
    
    solution = forms.CharField(
        label="Resolution / Solution Steps",
        widget=forms.Textarea(attrs={
            'class': INPUT_STYLE,
            'rows': 6,
            'placeholder': 'Provide step-by-step instructions to resolve the issue...\n\n1. First step\n2. Second step\n3. ...'
        })
    )
    
    internal_notes = forms.CharField(
        label="Internal IT Notes (Optional)",
        required=False,
        widget=forms.Textarea(attrs={
            'class': INPUT_STYLE,
            'rows': 3,
            'placeholder': 'Internal technical notes, known bugs, escalation info... (Only visible to Superusers)'
        })
    )
    
    status = forms.ChoiceField(
        label="Article Status",
        choices=STATUS_CHOICES,
        initial='Draft',
        widget=forms.Select(attrs={'class': INPUT_STYLE})
    )
    
    def __init__(self, *args, **kwargs):
        """
        Custom initialization to allow pre-populating form with existing article data.
        """
        initial_data = kwargs.get('initial', {})
        super().__init__(*args, **kwargs)
        
        # If editing an existing article, you can pre-populate fields here
        # Example: self.fields['category'].initial = initial_data.get('category')

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
    
    # Add avatar field (Manual handling for UserProfile)
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
        
        # Pre-fill avatar from UserProfile
        if self.instance.pk:
            try:
                if hasattr(self.instance, 'profile') and self.instance.profile.avatar:
                    self.initial['avatar'] = self.instance.profile.avatar
            except Exception:
                pass
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        # Handle Avatar Save
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Import here to avoid circular dependency if needed, or rely on top-level import
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.avatar = avatar
            profile.save()
        return user
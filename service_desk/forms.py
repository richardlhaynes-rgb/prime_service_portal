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

# --- 4. Printer & Scanner Form (New) ---
class PrinterScannerForm(forms.Form):
    # Based on your screenshot image_033bdf.png
    
    printer_location = forms.CharField(
        label="Printer/Scanner Location",
        widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': 'Location (e.g., "Lexington 1st Floor")'})
    )

    # In your screenshot, "Summary" is a big box, acting like a Description.
    description = forms.CharField(
        label="Summary of Problem",
        widget=forms.Textarea(attrs={'class': INPUT_STYLE + ' h-32', 'placeholder': "Please describe the problem in detail."})
    )

    computer_name = forms.CharField(
        required=False,
        label="Affected Computer (if not your own)",
        widget=forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': "Leave blank if it's your primary computer"})
    )
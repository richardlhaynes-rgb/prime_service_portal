from django.contrib import admin
from .models import (
    Ticket, Comment, UserProfile, GlobalSettings, 
    CSATSurvey, Notification, ServiceBoard, 
    ServiceType, ServiceSubtype, ServiceItem
)

# --- TAXONOMY ADMIN (ConnectWise Architecture) ---

@admin.register(ServiceBoard)
class ServiceBoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order', 'is_active', 'created_at')
    list_editable = ('sort_order', 'is_active')
    search_fields = ('name', 'description')
    filter_horizontal = ('members', 'restricted_groups', 'allowed_types')

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'form_class_name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(ServiceSubtype)
class ServiceSubtypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    filter_horizontal = ('parent_types',)

@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    filter_horizontal = ('parent_subtypes',)


# --- TICKET ADMIN (Updated) ---

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    # CHANGED: 'ticket_type' -> 'type' (The new ForeignKey)
    list_display = ('id', 'title', 'type', 'board', 'status', 'priority', 'submitter', 'created_at')
    
    # CHANGED: Updated filters to use new relationships
    list_filter = ('status', 'priority', 'board', 'type', 'created_at')
    
    # Updated search to look into related fields
    search_fields = ('title', 'description', 'submitter__username', 'submitter__email', 'type__name', 'subtype__name')
    
    readonly_fields = ('created_at', 'updated_at', 'closed_at', 'first_response_at')
    
    # Organization of fields in the edit page
    fieldsets = (
        ('Core Info', {
            'fields': ('title', 'description', 'submitter', 'technician', 'contact_email', 'contact_phone')
        }),
        ('Classification', {
            'fields': ('board', 'type', 'subtype', 'item', 'status', 'priority', 'source')
        }),
        ('Form Specific Data', {
            'fields': ('application_name', 'computer_name', 'asset_tag', 'software_name', 'justification'),
            'classes': ('collapse',) 
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'closed_at', 'first_response_at'),
            'classes': ('collapse',)
        }),
    )


# --- EXISTING & NEW HELPER ADMINS ---

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'author', 'created_at', 'is_internal')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('text', 'author__username')
    readonly_fields = ('created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'department', 'location', 'phone_office', 'created_at')
    list_filter = ('department', 'location', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'connectwise_id')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'connectwise_id')
        }),
        ('Professional Details', {
            'fields': ('title', 'department', 'location', 'hire_date')
        }),
        ('Contact Information', {
            'fields': ('phone_office', 'phone_mobile')
        }),
        ('Media', {
            'fields': ('avatar', 'bio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CSATSurvey)
class CSATSurveyAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'rating', 'submitted_by', 'submitted_at')
    list_filter = ('rating', 'submitted_at')
    readonly_fields = ('submitted_at',)

@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'maintenance_mode', 'support_phone', 'updated_at')
    
    def has_add_permission(self, request):
        # Prevent creating more than one settings object
        return not GlobalSettings.objects.exists()

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
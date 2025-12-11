from django.contrib import admin
from .models import Ticket, Comment, UserProfile


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'ticket_type', 'status', 'priority', 'submitter', 'created_at')
    list_filter = ('ticket_type', 'status', 'priority', 'created_at')
    search_fields = ('title', 'description', 'submitter__username')
    readonly_fields = ('created_at', 'updated_at')


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

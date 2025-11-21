from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'updated_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'problem', 'solution')
    readonly_fields = ('created_at', 'updated_at')
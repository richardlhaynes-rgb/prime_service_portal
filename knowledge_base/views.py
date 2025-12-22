from django.shortcuts import render, redirect
from django.contrib import messages

# --- IMPORT THE CORRECT SERVICE LAYER ---
from services import ticket_service

def kb_home(request):
    """
    Knowledge Base Home: Search and browse articles with icon mapping and category filtering.
    
    This view fetches articles from ticket_service.get_knowledge_base_articles(),
    which automatically injects the 'icon' property based on subcategory.
    
    Args:
        request: HTTP request object
    
    Returns:
        Rendered kb_home.html template with articles list
    """
    # Get search query and category filter from URL parameters
    search_query = request.GET.get('q')
    category_filter = request.GET.get('category')
    
    # *** CRITICAL FIX: Use ticket_service.get_knowledge_base_articles() ***
    # This function injects the 'icon' property that the template expects
    articles = ticket_service.get_knowledge_base_articles(search_query=search_query)
    
    # *** NEW: Filter by category if specified ***
    if category_filter:
        articles = [a for a in articles if a.get('category') == category_filter]
    
    # Limit to 10 most recent for display
    recent_articles = sorted(
        articles, 
        key=lambda x: x.get('updated_at', ''), 
        reverse=True
    )[:10]
    
    return render(request, 'knowledge_base/kb_home.html', {
        'articles': articles,
        'recent_articles': recent_articles,
        'search_query': search_query,
        'current_category': category_filter
    })

# NOTE: article_detail view is now handled by service_desk/views.py
# The URL routing in knowledge_base/urls.py should point to the service_desk version
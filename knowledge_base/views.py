from django.shortcuts import render, redirect
from django.contrib import messages

# --- IMPORT THE CORRECT SERVICE LAYER ---
from services import ticket_service

def kb_home(request):
    """
    Knowledge Base Home: Search and browse articles with icon mapping.
    
    This view fetches articles from ticket_service.get_knowledge_base_articles(),
    which automatically injects the 'icon' property based on subcategory.
    
    Args:
        request: HTTP request object
    
    Returns:
        Rendered kb_home.html template with articles list
    """
    # Get search query from URL parameter
    search_query = request.GET.get('q')
    
    # *** CRITICAL FIX: Use ticket_service.get_knowledge_base_articles() ***
    # This function injects the 'icon' property that the template expects
    articles = ticket_service.get_knowledge_base_articles(search_query=search_query)
    
    # Limit to 10 most recent for display
    recent_articles = sorted(
        articles, 
        key=lambda x: x.get('updated_at', ''), 
        reverse=True
    )[:10]
    
    return render(request, 'knowledge_base/kb_home.html', {
        'recent_articles': recent_articles,
        'search_query': search_query
    })


def article_detail(request, pk):
    """
    Displays a single KB article.
    
    Args:
        pk: Article ID (from URL)
    
    Returns:
        Rendered article_detail.html template or redirect to KB home if not found
    """
    # Fetch all articles (with icon mapping applied)
    articles = ticket_service.get_knowledge_base_articles()
    
    # Find the specific article by ID
    article = next((a for a in articles if a['id'] == pk), None)
    
    if not article:
        messages.error(request, "Article not found.")
        return redirect('kb_home')
    
    return render(request, 'knowledge_base/article_detail.html', {
        'article': article
    })
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Article

# --- IMPORT THE SERVICE LAYER ---
from services import kb_service

def kb_home(request):
    query = request.GET.get('q')
    
    # Use the Service Layer
    articles = kb_service.get_all_articles(search_query=query)
    
    # Limit to 10 most recent
    if kb_service.USE_MOCK_DATA:
        recent_articles = sorted(articles, key=lambda x: x.get('updated_at', ''), reverse=True)[:10]
    else:
        recent_articles = articles[:10]
    
    return render(request, 'knowledge_base/kb_home.html', {
        'recent_articles': recent_articles,
        'search_query': query
    })

def article_detail(request, pk):
    article = kb_service.get_article_by_id(pk)
    
    if not article:
        messages.error(request, "Article not found.")
        from django.shortcuts import redirect
        return redirect('kb_home')
    
    return render(request, 'knowledge_base/article_detail.html', {'article': article})
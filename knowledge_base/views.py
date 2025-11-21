from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Article

def kb_home(request):
    query = request.GET.get('q')
    # Show only approved articles
    articles = Article.objects.filter(status=Article.Status.APPROVED)

    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(subcategory__icontains=query) |
            Q(problem__icontains=query) |
            Q(solution__icontains=query)
        )
    
    recent_articles = articles.order_by('-updated_at')[:10]
    return render(request, 'knowledge_base/kb_home.html', {'recent_articles': recent_articles, 'search_query': query})

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, status=Article.Status.APPROVED)
    return render(request, 'knowledge_base/article_detail.html', {'article': article})
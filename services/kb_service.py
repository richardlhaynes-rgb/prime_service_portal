import json
import os
from django.conf import settings
from knowledge_base.models import Article

# --- TOGGLE: Demo Mode vs Live Data ---
USE_MOCK_DATA = True

def get_all_articles(search_query=None):
    """
    Returns all approved KB articles.
    If USE_MOCK_DATA is True, returns data from JSON file.
    Otherwise, queries the database.
    """
    if USE_MOCK_DATA:
        # Load from JSON
        json_path = os.path.join(settings.BASE_DIR, 'data', 'mock_articles.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            articles_data = json.load(f)
        
        # Filter by search query if provided
        if search_query:
            query_lower = search_query.lower()
            articles_data = [
                article for article in articles_data
                if query_lower in article['title'].lower() or
                   query_lower in article['subcategory'].lower() or
                   query_lower in article['problem'].lower() or
                   query_lower in article['solution'].lower()
            ]
        
        # Return only approved articles (though all in mock are approved)
        return [a for a in articles_data if a['status'] == 'Approved']
    else:
        # Query the database
        articles = Article.objects.filter(status=Article.Status.APPROVED)
        
        if search_query:
            from django.db.models import Q
            articles = articles.filter(
                Q(title__icontains=search_query) |
                Q(subcategory__icontains=search_query) |
                Q(problem__icontains=search_query) |
                Q(solution__icontains=search_query)
            )
        
        return articles.order_by('-updated_at')

def get_article_by_id(article_id):
    """
    Retrieves a single KB article by ID.
    """
    if USE_MOCK_DATA:
        json_path = os.path.join(settings.BASE_DIR, 'data', 'mock_articles.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            articles_data = json.load(f)
        
        # Find the article with matching ID
        for article in articles_data:
            if article['id'] == article_id:
                return article
        return None
    else:
        try:
            return Article.objects.get(pk=article_id, status=Article.Status.APPROVED)
        except Article.DoesNotExist:
            return None
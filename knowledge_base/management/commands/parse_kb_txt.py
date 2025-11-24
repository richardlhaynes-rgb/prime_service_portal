import os
import re
import json
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Parses kb_source.txt and generates mock_articles.json'

    def handle(self, *args, **kwargs):
        source_file = os.path.join(settings.BASE_DIR, 'data', 'kb_source.txt')
        output_file = os.path.join(settings.BASE_DIR, 'data', 'mock_articles.json')

        if not os.path.exists(source_file):
            self.stdout.write(self.style.ERROR(f"❌ File not found: {source_file}"))
            return

        self.stdout.write(self.style.WARNING("📖 Reading kb_source.txt..."))

        # Read the file
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by "Article X" headers
        raw_articles = re.split(r'\n\s*Article \d+\s*\n', content)
        
        articles = []
        article_id = 1

        for raw in raw_articles:
            if not raw.strip():
                continue

            # Extract fields using regex
            title_match = re.search(r'KB Title:\s*(.+)', raw)
            category_match = re.search(r'Category:\s*(.+)', raw)
            subcategory_match = re.search(r'Subcategory:\s*(.+)', raw)
            problem_match = re.search(r'Problem:\s*(.+?)(?=\nSolution:|\Z)', raw, re.DOTALL)
            solution_match = re.search(r'Solution:\s*(.+?)(?=\nSource:|\nArticle \d+|\Z)', raw, re.DOTALL)

            if not title_match:
                continue  # Skip malformed entries

            # Extract and clean data
            title = title_match.group(1).strip()
            category = category_match.group(1).strip() if category_match else "General"
            subcategory = subcategory_match.group(1).strip() if subcategory_match else "General"
            problem = problem_match.group(1).strip() if problem_match else "No description provided."
            solution = solution_match.group(1).strip() if solution_match else "No solution provided."

            # Create JSON object
            article = {
                "id": article_id,
                "title": title,
                "category": category,
                "subcategory": subcategory,
                "status": "Approved",
                "problem": problem,
                "solution": solution,
                "created_at": "2025-01-15T10:00:00Z",
                "updated_at": "2025-01-15T10:00:00Z"
            }

            articles.append(article)
            self.stdout.write(self.style.SUCCESS(f"✅ Parsed: {title}"))
            article_id += 1

        # Write to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=4, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Successfully exported {len(articles)} articles to {output_file}"))
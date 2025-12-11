import os
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from knowledge_base.models import Article

class Command(BaseCommand):
    help = 'Parses kb_source.txt with explicit IDs, imports to DB, and regenerates mock_articles.json'

    SOURCE_FILE = os.path.join(settings.BASE_DIR, 'data', 'kb_source.txt')
    OUTPUT_JSON = os.path.join(settings.BASE_DIR, 'data', 'mock_articles.json')

    def handle(self, *args, **options):
        if not os.path.exists(self.SOURCE_FILE):
            self.stdout.write(self.style.ERROR(f"Source file not found: {self.SOURCE_FILE}"))
            return

        self.stdout.write(self.style.WARNING("🗑️  Clearing existing KB articles..."))
        Article.objects.all().delete()

        with open(self.SOURCE_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        articles = []
        current_article = None
        current_category = 'Internal IT Processes'
        current_subcategory = 'General'
        field_buffer = []
        active_field = None

        for line in lines:
            line = line.rstrip('\n\r')

            # State management: Category/Subcategory headers
            if line.startswith('Category:'):
                current_category = line.split(':', 1)[1].strip()
                continue
            elif line.startswith('Subcategory:'):
                current_subcategory = line.split(':', 1)[1].strip()
                continue

            # Article trigger: "ID: X"
            if line.startswith('ID:'):
                # Save previous article if exists
                if current_article:
                    self._finalize_field(current_article, active_field, field_buffer)
                    articles.append(current_article)

                # Start new article
                article_id = int(line.split(':', 1)[1].strip())
                current_article = {
                    'id': article_id,
                    'category': current_category,
                    'subcategory': current_subcategory,
                    'title': '',
                    'status': '',
                    'problem': '',
                    'solution': '',
                    'internal_notes': '',
                    'views': 0,
                    'helpful_votes': 0,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'author': 'Richard Haynes',
                    'tags': []
                }
                field_buffer = []
                active_field = None
                continue

            # Field headers
            if line.startswith('KB Title:'):
                self._finalize_field(current_article, active_field, field_buffer)
                current_article['title'] = line.split(':', 1)[1].strip()
                active_field = None
                field_buffer = []
                continue
            elif line.startswith('Status:'):
                self._finalize_field(current_article, active_field, field_buffer)
                current_article['status'] = line.split(':', 1)[1].strip()
                active_field = None
                field_buffer = []
                continue
            elif line.startswith('Problem:'):
                self._finalize_field(current_article, active_field, field_buffer)
                active_field = 'problem'
                field_buffer = [line.split(':', 1)[1].strip()]
                continue
            elif line.startswith('Solution:'):
                self._finalize_field(current_article, active_field, field_buffer)
                active_field = 'solution'
                field_buffer = [line.split(':', 1)[1].strip()]
                continue
            elif line.startswith('Notes:'):
                self._finalize_field(current_article, active_field, field_buffer)
                active_field = 'internal_notes'
                field_buffer = [line.split(':', 1)[1].strip()]
                continue

            # Continuation lines (append to buffer if inside a field)
            if active_field and current_article:
                field_buffer.append(line)

        # Save final article
        if current_article:
            self._finalize_field(current_article, active_field, field_buffer)
            articles.append(current_article)

        # Write to database
        created_count = 0
        for article_data in articles:
            Article.objects.create(
                id=article_data['id'],
                title=article_data['title'],
                category=article_data['category'],
                subcategory=article_data['subcategory'],
                problem=article_data['problem'],
                solution=article_data['solution'],
                internal_notes=article_data['internal_notes'],
                status=self._map_status(article_data['status'])
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Imported Article #{article_data['id']}: {article_data['title']}"))

        # Write to JSON
        with open(self.OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=4, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Import complete: {created_count} articles created.\n"
            f"📄 JSON regenerated: {self.OUTPUT_JSON}"
        ))

    def _finalize_field(self, article, field_name, buffer):
        """Joins buffered lines and assigns to article field."""
        if not article or not field_name:
            return
        article[field_name] = '\n'.join(buffer).strip()

    def _map_status(self, status_str):
        """Maps text status to Article.Status enum."""
        mapping = {
            'Approved': Article.Status.APPROVED,
            'Draft': Article.Status.DRAFT,
            'Pending Approval': Article.Status.PENDING,
            'Pending': Article.Status.PENDING  # Fallback
        }
        return mapping.get(status_str, Article.Status.DRAFT)
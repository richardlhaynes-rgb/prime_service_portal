import os
import re
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from knowledge_base.models import Article

class Command(BaseCommand):
    help = 'Imports KB articles from kb_source.txt, populates internal_notes, and regenerates mock_articles.json'

    SOURCE_FILENAME = os.path.join(settings.BASE_DIR, 'data', 'kb_source.txt')
    OUTPUT_JSON = os.path.join(settings.BASE_DIR, 'data', 'mock_articles.json')

    ARTICLE_REGEX = re.compile(
        r'(?:Category:\s*(?P<category>.+?)\r?\n)?'
        r'(?:Subcategory:\s*(?P<subcategory>.+?)\r?\n)?'
        r'Article\s+(?P<number>\d+)\r?\n'
        r'KB Title:\s*(?P<title>.+?)\r?\n'
        r'Problem:\s*(?P<problem>.*?)(?=\r?\nSolution:)'
        r'\r?\nSolution:\s*(?P<solution>.*?)(?:\r?\nSource \(for internal reference\):\s*(?P<source>.+))?'
        r'(?=\r?\nCategory:|\r?\nSubcategory:|\r?\nArticle\s+\d+|\Z)',
        re.DOTALL
    )

    def handle(self, *args, **options):
        if not os.path.exists(self.SOURCE_FILENAME):
            self.stdout.write(self.style.ERROR(f"File not found: {self.SOURCE_FILENAME}"))
            return

        self.stdout.write(self.style.WARNING("Wiping existing Knowledge Base articles..."))
        Article.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Existing KB data cleared."))

        with open(self.SOURCE_FILENAME, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = list(self.ARTICLE_REGEX.finditer(content))
        self.stdout.write(self.style.NOTICE(f"Found {len(matches)} article blocks."))

        articles_json = []
        created_count = 0

        for m in matches:
            raw_category = (m.group('category') or '').strip()
            raw_subcategory = (m.group('subcategory') or '').strip()
            title = m.group('title').strip()
            problem = self._clean_multiline(m.group('problem'))
            solution = self._clean_multiline(m.group('solution'))
            source = (m.group('source') or '').strip()

            # Fallbacks
            category = raw_category if raw_category else 'Internal IT Processes'
            subcategory = raw_subcategory if raw_subcategory else 'General'

            # internal_notes populated from Source line
            internal_notes = source

            # Create DB record (status defaults to Approved)
            article_obj = Article.objects.create(
                title=title,
                category=category,
                subcategory=subcategory,
                problem=problem,
                solution=solution,
                internal_notes=internal_notes,
                status=Article.Status.APPROVED
            )
            created_count += 1

            articles_json.append({
                "id": article_obj.id,
                "title": title,
                "category": category,
                "subcategory": subcategory,
                "status": "Approved",
                "problem": problem,
                "solution": solution,
                "internal_notes": internal_notes,
                "views": 0,
                "helpful_votes": 0,
                "created_at": article_obj.created_at.isoformat(),
                "updated_at": article_obj.updated_at.isoformat()
            })

            self.stdout.write(self.style.SUCCESS(f"Imported: {title}"))

        # Regenerate mock_articles.json
        with open(self.OUTPUT_JSON, 'w', encoding='utf-8') as jf:
            json.dump(articles_json, jf, indent=4, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(
            f"Completed import. Created {created_count} articles. "
            f"Regenerated JSON: {self.OUTPUT_JSON}"
        ))

    @staticmethod
    def _clean_multiline(text):
        if not text:
            return ''
        # Strip leading/trailing whitespace, normalize Windows line endings
        cleaned = text.replace('\r\n', '\n').strip()
        # Remove any trailing blank lines
        return re.sub(r'\n{3,}', '\n\n', cleaned)
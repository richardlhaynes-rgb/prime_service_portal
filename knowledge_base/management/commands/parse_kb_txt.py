import os
import re
import json
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Parses data/kb_source.txt and generates data/mock_articles.json with internal_notes from "Source (for internal reference)" lines.'

    def handle(self, *args, **kwargs):
        source_file = os.path.join(settings.BASE_DIR, 'data', 'kb_source.txt')
        output_file = os.path.join(settings.BASE_DIR, 'data', 'mock_articles.json')

        if not os.path.exists(source_file):
            self.stdout.write(self.style.ERROR(f"File not found: {source_file}"))
            return

        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into blocks by Article N headers (keep content before first Article if present)
        blocks = re.split(r'\r?\nArticle\s+\d+\s*\r?\n', content)

        articles = []
        article_id = 1

        for raw in blocks:
            raw = raw.strip()
            if not raw:
                continue

            # Extract fields
            category_match = re.search(r'Category:\s*(.+)', raw)
            subcategory_match = re.search(r'Subcategory:\s*(.+)', raw)
            title_match = re.search(r'KB Title:\s*(.+)', raw)

            problem_match = re.search(r'Problem:\s*(.+?)(?=\r?\nSolution:|\Z)', raw, re.DOTALL)

            # Updated Solution regex: stop before Source line, next Article, or end
            solution_match = re.search(
                r'Solution:\s*(.+?)(?=\r?\nSource\s*\(for internal reference\)\s*:|\r?\nArticle\s+\d+|\Z)',
                raw,
                re.DOTALL
            )

            # Internal Notes from the Source line
            source_match = re.search(r'Source\s*\(for internal reference\)\s*:\s*(.+)', raw)

            # Title required
            if not title_match:
                continue

            title = title_match.group(1).strip()
            category = (category_match.group(1).strip() if category_match else "Internal IT Processes")
            subcategory = (subcategory_match.group(1).strip() if subcategory_match else "General")
            problem = _clean_multiline(problem_match.group(1) if problem_match else "")
            solution = _clean_multiline(solution_match.group(1) if solution_match else "")
            internal_notes = source_match.group(1).strip() if source_match else ""

            article = {
                "id": article_id,
                "title": title,
                "category": category,
                "subcategory": subcategory,
                "status": "Approved",
                "problem": problem,
                "solution": solution,
                "internal_notes": internal_notes,
                "views": 0,
                "helpful_votes": 0,
                # Static timestamps for demo data; DB-backed import uses real times
                "created_at": "2025-01-15T10:00:00Z",
                "updated_at": "2025-01-15T10:00:00Z"
            }
            articles.append(article)
            article_id += 1

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=4, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"Exported {len(articles)} articles to {output_file}"))

def _clean_multiline(text: str) -> str:
    if not text:
        return ""
    cleaned = text.replace('\r\n', '\n').strip()
    return re.sub(r'\n{3,}', '\n\n', cleaned)
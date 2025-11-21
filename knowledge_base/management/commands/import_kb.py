import re
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from knowledge_base.models import Article

class Command(BaseCommand):
    help = 'Imports KB articles from kb_source.md and wipes existing data'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'kb_source.md')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        # 1. WIPE EXISTING DATA
        self.stdout.write(self.style.WARNING("Wiping existing Knowledge Base articles..."))
        Article.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Old data deleted."))

        # 2. READ FILE
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 3. PARSE
        # Split by "Article X" header
        raw_articles = re.split(r'Article \d+', content)
        count = 0

        for raw in raw_articles:
            if not raw.strip():
                continue

            # Regex to find specific fields
            title_match = re.search(r'KB Title:\s*(.*?)\n', raw)
            problem_match = re.search(r'Problem:\s*(.*?)(?=Solution:)', raw, re.DOTALL)
            solution_match = re.search(r'Solution:\s*(.*?)(?=Source|Article|$)', raw, re.DOTALL)

            if title_match:
                title = title_match.group(1).strip()
                # Default to empty strings if not found
                problem = problem_match.group(1).strip() if problem_match else "No description provided."
                solution = solution_match.group(1).strip() if solution_match else "No solution provided."

                # --- Auto-Categorizer ---
                category = Article.Category.INTERNAL_PROCESS # Default
                subcategory = "General"
                t_lower = title.lower()

                if any(x in t_lower for x in ['autocad', 'revit', 'bluebeam', 'civil 3d', '3ds max', 'sketchup', 'navisworks']):
                    category = Article.Category.DESIGN_APPS
                    subcategory = "Design Software"
                elif any(x in t_lower for x in ['outlook', 'excel', 'word', 'teams', 'onedrive', 'office', 'powerpoint']):
                    category = Article.Category.BUSINESS_ADMIN
                    subcategory = "Microsoft 365"
                elif any(x in t_lower for x in ['printer', 'plotter', 'scanner', 'xerox', 'papercut']):
                    category = Article.Category.PRINTING
                    subcategory = "Printing & Plotting"
                elif any(x in t_lower for x in ['vpn', 'wifi', 'internet', 'network', 'forticlient']):
                    category = Article.Category.NETWORKING
                    subcategory = "Network Access"
                elif any(x in t_lower for x in ['laptop', 'monitor', 'dock', 'mouse', 'keyboard', 'screen']):
                    category = Article.Category.HARDWARE
                    subcategory = "Hardware"
                elif any(x in t_lower for x in ['password', 'mfa', 'login', 'account']):
                    category = Article.Category.SECURITY
                    subcategory = "Account Security"

                # Create Article
                Article.objects.create(
                    title=title,
                    problem=problem,
                    solution=solution,
                    category=category,
                    subcategory=subcategory,
                    status=Article.Status.APPROVED
                )
                self.stdout.write(f"Imported: {title}")
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} articles!"))
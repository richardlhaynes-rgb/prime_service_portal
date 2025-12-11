from django.core.management.base import BaseCommand
from knowledge_base.models import Article, KBCategory, KBSubcategory

class Command(BaseCommand):
    help = 'Migrates KB Article categories from text fields to database models'

    def handle(self, *args, **kwargs):
        articles = Article.objects.all()
        migrated_count = 0
        skipped_count = 0
        
        self.stdout.write(self.style.NOTICE(f"Found {articles.count()} articles. Starting migration..."))

        for article in articles:
            try:
                # Skip if already migrated
                if article.category_fk and article.subcategory_fk:
                    skipped_count += 1
                    continue

                # 1. Migrate Category (Text → FK)
                if article.category:
                    cat_name = article.category.strip()
                    kb_cat, cat_created = KBCategory.objects.get_or_create(
                        name=cat_name,
                        defaults={'sort_order': 0}
                    )
                    article.category_fk = kb_cat
                    if cat_created:
                        self.stdout.write(f"  ✓ Created category: {cat_name}")

                    # 2. Migrate Subcategory (Text → FK)
                    if article.subcategory:
                        sub_name = article.subcategory.strip()
                        kb_sub, sub_created = KBSubcategory.objects.get_or_create(
                            name=sub_name,
                            parent=kb_cat,
                            defaults={'sort_order': 0}
                        )
                        article.subcategory_fk = kb_sub
                        if sub_created:
                            self.stdout.write(f"    ✓ Created subcategory: {sub_name}")

                article.save(update_fields=['category_fk', 'subcategory_fk'])
                migrated_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error migrating article #{article.id}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Migration Complete!\n'
                f'  Migrated: {migrated_count} articles\n'
                f'  Already migrated: {skipped_count} articles'
            )
        )
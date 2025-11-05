from django.core.management.base import BaseCommand
from django.db import transaction

from clothes.models import Product, Category, ProductImage, Size
from order.models import OrderItem


class Command(BaseCommand):
    help = (
        "Scan for and optionally fix broken foreign key references related to products, "
        "including OrderItem.product, ProductImage.product, and Product.sizes through table."
    )
    # Allow running this command even if Pillow isn't installed (skip system checks)
    requires_system_checks = []
    requires_migrations_checks = False

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Apply fixes instead of just reporting problems.",
        )
        parser.add_argument(
            "--create-uncategorized",
            action="store_true",
            help=(
                "If products are found with invalid category_id, create/use an 'Uncategorized' "
                "category and reassign them."
            ),
        )

    def handle(self, *args, **options):
        fix = options["fix"]
        create_uncategorized = options["create_uncategorized"]

        self.stdout.write(self.style.NOTICE("Collecting current IDs..."))
        product_ids = set(Product.objects.values_list("id", flat=True))
        category_ids = set(Category.objects.values_list("id", flat=True))
        size_ids = set(Size.objects.values_list("id", flat=True))

        # 1) Orphan OrderItem.product references
        orphan_orderitems = (
            OrderItem.objects
            .filter(product_id__isnull=False)
            .exclude(product_id__in=product_ids)
        )
        oi_count = orphan_orderitems.count()
        if oi_count:
            self.stdout.write(self.style.WARNING(f"Found {oi_count} OrderItem(s) with missing Product."))
            if fix:
                with transaction.atomic():
                    updated = orphan_orderitems.update(product=None)
                self.stdout.write(self.style.SUCCESS(f"Set product=None on {updated} OrderItem(s)."))

        else:
            self.stdout.write(self.style.SUCCESS("No orphaned OrderItem.product rows found."))

        # 2) Orphan ProductImage.product references
        orphan_images = (
            ProductImage.objects
            .filter(product_id__isnull=False)
            .exclude(product_id__in=product_ids)
        )
        img_count = orphan_images.count()
        if img_count:
            self.stdout.write(self.style.WARNING(f"Found {img_count} ProductImage(s) with missing Product."))
            if fix:
                with transaction.atomic():
                    deleted, _ = orphan_images.delete()
                self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} dangling ProductImage(s)."))
        else:
            self.stdout.write(self.style.SUCCESS("No orphaned ProductImage.product rows found."))

        # 3) Orphan entries in Product.sizes through table
        through = Product.sizes.through
        orphan_ps_product = (
            through.objects
            .exclude(product_id__in=product_ids)
        )
        orphan_ps_size = (
            through.objects
            .exclude(size_id__in=size_ids)
        )

        orphan_ps_product_count = orphan_ps_product.count()
        orphan_ps_size_count = orphan_ps_size.count()

        if orphan_ps_product_count or orphan_ps_size_count:
            self.stdout.write(
                self.style.WARNING(
                    f"Found {orphan_ps_product_count} m2m rows with missing product and "
                    f"{orphan_ps_size_count} m2m rows with missing size."
                )
            )
            if fix:
                with transaction.atomic():
                    del1, _ = orphan_ps_product.delete()
                    del2, _ = orphan_ps_size.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Deleted {del1} product-orphan and {del2} size-orphan m2m rows."
                    )
                )
        else:
            self.stdout.write(self.style.SUCCESS("No orphaned product-size m2m rows found."))

        # 4) Products with invalid category_id
        products_invalid_category = Product.objects.exclude(category_id__in=category_ids)
        pic_count = products_invalid_category.count()
        if pic_count:
            self.stdout.write(self.style.WARNING(f"Found {pic_count} Product(s) with invalid category_id."))
            if fix and create_uncategorized:
                uncategorized, _ = Category.objects.get_or_create(name="Uncategorized")
                with transaction.atomic():
                    reassigned = products_invalid_category.update(category=uncategorized)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Reassigned {reassigned} Product(s) to Category '{uncategorized.name}'."
                    )
                )
            elif fix and not create_uncategorized:
                self.stdout.write(
                    self.style.NOTICE(
                        "--fix provided but --create-uncategorized not set; "
                        "skipping reassignment of products with invalid categories."
                    )
                )
        else:
            self.stdout.write(self.style.SUCCESS("All Products have valid categories."))

        if not any([oi_count, img_count, orphan_ps_product_count, orphan_ps_size_count, pic_count]):
            self.stdout.write(self.style.SUCCESS("No integrity issues detected."))
        else:
            if not fix:
                self.stdout.write(
                    self.style.WARNING(
                        "Issues detected. Re-run with --fix (and optionally --create-uncategorized) to apply repairs."
                    )
                )

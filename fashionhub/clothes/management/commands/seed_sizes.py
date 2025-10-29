from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Create standard sizes (M,L,XL,XXL) and optionally assign them to all products'

    def add_arguments(self, parser):
        parser.add_argument('--assign-all', action='store_true', help='Assign all created sizes to all products')

    def handle(self, *args, **options):
        from clothes.models import Size, Product

        names = ['M', 'L', 'XL', 'XXL']
        created = []
        for name in names:
            size, _ = Size.objects.get_or_create(name=name)
            created.append(size)

        self.stdout.write(self.style.SUCCESS(f'Created/ensured sizes: {", ".join(n.name for n in created)}'))

        if options.get('assign_all'):
            products = Product.objects.all()
            for p in products:
                p.sizes.add(*created)
            self.stdout.write(self.style.SUCCESS(f'Assigned sizes to {products.count()} products'))

        self.stdout.write(self.style.NOTICE('Done. Use the admin to fine-tune sizes per product.'))

import os
import shutil
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from apps.store.models import (
    Announcement, Category, Collection, Tag,
    Product, ProductVariant, ProductVariantSize,
    ProductDetail, ProductDimension,
    LookBook, LookBookImage,
)


def copy_placeholder(src, dest_relative):
    """Copy placeholder.jpg to a destination relative to MEDIA_ROOT."""
    dest = os.path.join(settings.MEDIA_ROOT, dest_relative)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(src, dest)
    return dest_relative


def make_variant(product, variant_name, sizes, sku_counter):
    """
    Create a ProductVariant + one ProductVariantSize per size entry.

    sizes: list of (size_str, stock_int) tuples
           e.g. [('S', 10), ('M', 10), ('L', 5)]

    Returns the updated sku_counter.
    """
    variant = ProductVariant.objects.create(
        product=product,
        name=variant_name,
        is_active=True,
    )
    for size_str, stock in sizes:
        ProductVariantSize.objects.create(
            variant=variant,
            size=size_str,
            sku=f'KR-{sku_counter:04d}',
            stock=stock,
            is_active=True,
        )
        sku_counter += 1
    return sku_counter


class Command(BaseCommand):
    help = 'Seed the database with sample Kira data'

    def handle(self, *args, **kwargs):
        placeholder = os.path.join(settings.MEDIA_ROOT, 'placeholder.jpg')

        if not os.path.exists(placeholder):
            self.stdout.write(self.style.ERROR(
                'Missing media/placeholder.jpg — add one image file before seeding.'
            ))
            return

        self.stdout.write('Seeding...')

        # ─── ANNOUNCEMENTS ───
        Announcement.objects.all().delete()
        Announcement.objects.create(
            message='Complimentary shipping on all orders above £500',
            link_text='Shop Now',
            link_url='/products/',
            is_active=True,
        )
        Announcement.objects.create(
            message='SS 2025 Collection — Now Available',
            link_text='Discover',
            link_url='/collections/ss-2025/',
            is_active=True,
        )

        # ─── CATEGORIES ───
        Category.objects.all().delete()
        cat_data = [
            ('Ready to Wear', 0),
            ('Accessories',   1),
            ('Footwear',      2),
            ('Jewellery',     3),
        ]
        categories = {}
        for name, order in cat_data:
            c = Category.objects.create(name=name, slug=slugify(name), order=order)
            categories[name] = c
        self.stdout.write('  Categories done')

        # ─── COLLECTIONS ───
        Collection.objects.all().delete()
        col_data = [
            ('Atelier Signature', 'atelier-signature', 'Our flagship ready-to-wear line. Structured silhouettes, restrained palette.', 0, True, True),
            ('Voyage',            'voyage',            'Travel essentials conceived for the modern nomad.',                            1, True, False),
            ("Bijoux d'Élite",    'bijoux-d-elite',    'Fine jewellery — each piece cast in 18k gold and hand-set stones.',            2, True, False),
            ('SS 2025',           'ss-2025',           'The Spring/Summer 2025 seasonal collection.',                                  3, True, True),
        ]
        collections = {}
        for name, slug, desc, order, active, featured in col_data:
            img_path = copy_placeholder(placeholder, f'collections/{slug}.jpg')
            c = Collection.objects.create(
                name=name,
                slug=slug,
                description=desc,
                order=order,
                is_active=active,
                is_featured=featured,
                image=img_path,
            )
            collections[name] = c
        self.stdout.write('  Collections done')

        # ─── TAGS ───
        Tag.objects.all().delete()
        tag_names = ['Handcrafted', 'Limited Edition', 'Sustainable', 'New Season', 'Bestseller', 'Exclusive']
        tags = {}
        for name in tag_names:
            t = Tag.objects.create(name=name, slug=slugify(name))
            tags[name] = t
        self.stdout.write('  Tags done')

        # ─── PRODUCTS ───
        Product.objects.all().delete()
        product_data = [
            {
                'name':           'Le Manteau Croisé',
                'collection':     'Atelier Signature',
                'category':       'Ready to Wear',
                'description':    'A double-breasted overcoat in wool-cashmere blend. Structured shoulders, satin lining, horn buttons. The definitive Kira silhouette.',
                'price':          '1850.00',
                'badge':          'SS 2025',
                'tags':           ['New Season', 'Handcrafted'],
                'is_featured':    True,
                'is_new_arrival': True,
                'is_trending':    False,
            },
            {
                'name':           'La Robe Colonne',
                'collection':     'Atelier Signature',
                'category':       'Ready to Wear',
                'description':    'Column dress in silk crêpe. Bias-cut for a fluid fall. Invisible zip, fully lined. A study in quiet authority.',
                'price':          '2200.00',
                'badge':          'New',
                'tags':           ['New Season', 'Exclusive'],
                'is_featured':    True,
                'is_new_arrival': True,
                'is_trending':    True,
            },
            {
                'name':           'Le Blazer Atelier',
                'collection':     'Atelier Signature',
                'category':       'Ready to Wear',
                'description':    'Single-button blazer in Italian virgin wool. Patch pockets, hand-stitched lapels. Built to last decades.',
                'price':          '1450.00',
                'badge':          '',
                'tags':           ['Handcrafted', 'Bestseller'],
                'is_featured':    True,
                'is_new_arrival': False,
                'is_trending':    True,
            },
            {
                'name':           'Le Pantalon Tailleur',
                'collection':     'Atelier Signature',
                'category':       'Ready to Wear',
                'description':    'High-waisted tailored trousers. Pressed centre crease, side-adjusters, half-lined. Pairs with the Blazer Atelier.',
                'price':          '780.00',
                'badge':          '',
                'tags':           ['Handcrafted'],
                'is_featured':    False,
                'is_new_arrival': False,
                'is_trending':    True,
            },
            {
                'name':           'Le Sac Voyage',
                'collection':     'Voyage',
                'category':       'Accessories',
                'description':    'Weekender in full-grain vegetable-tanned leather. Brass hardware, cotton canvas lining. Ages beautifully.',
                'price':          '3200.00',
                'badge':          'Limited',
                'tags':           ['Handcrafted', 'Limited Edition'],
                'is_featured':    True,
                'is_new_arrival': True,
                'is_trending':    False,
            },
            {
                'name':           'Le Portefeuille Long',
                'collection':     'Voyage',
                'category':       'Accessories',
                'description':    'Long wallet in smooth calfskin. 12 card slots, zip coin pocket, press-stud closure.',
                'price':          '490.00',
                'badge':          '',
                'tags':           ['Bestseller'],
                'is_featured':    False,
                'is_new_arrival': False,
                'is_trending':    True,
            },
            {
                'name':           'Bague Soleil',
                'collection':     "Bijoux d'Élite",
                'category':       'Jewellery',
                'description':    '18k yellow gold ring. Central pavé diamond cluster, hand-set by our Parisian atelier. Sold with certificate.',
                'price':          '4800.00',
                'badge':          'Exclusive',
                'tags':           ['Exclusive', 'Handcrafted', 'Limited Edition'],
                'is_featured':    True,
                'is_new_arrival': True,
                'is_trending':    False,
            },
            {
                'name':           'Collier Lune',
                'collection':     "Bijoux d'Élite",
                'category':       'Jewellery',
                'description':    'White gold chain with crescent moon pendant. 42cm adjustable length. Diamonds along the inner edge.',
                'price':          '3600.00',
                'badge':          'New',
                'tags':           ['New Season', 'Exclusive'],
                'is_featured':    False,
                'is_new_arrival': True,
                'is_trending':    True,
            },
            {
                'name':           "L'Escarpin Signature",
                'collection':     'SS 2025',
                'category':       'Footwear',
                'description':    '85mm heel pump in nude calfskin. Pointed toe, leather sole, padded insole. The house heel.',
                'price':          '920.00',
                'badge':          'SS 2025',
                'tags':           ['New Season', 'Bestseller'],
                'is_featured':    True,
                'is_new_arrival': True,
                'is_trending':    True,
            },
            {
                'name':           'La Mule Dorée',
                'collection':     'SS 2025',
                'category':       'Footwear',
                'description':    'Flat mule in gold metallic leather. Open toe, elasticated back strap, suede lining. Summer ease.',
                'price':          '650.00',
                'badge':          'SS 2025',
                'tags':           ['New Season'],
                'is_featured':    False,
                'is_new_arrival': True,
                'is_trending':    False,
            },
        ]

        products = {}
        for d in product_data:
            slug = slugify(d['name'])
            img_path = copy_placeholder(placeholder, f'products/{slug}.jpg')
            p = Product.objects.create(
                name=d['name'],
                slug=slug,
                collection=collections[d['collection']],
                category=categories[d['category']],
                description=d['description'],
                price=d['price'],
                badge=d['badge'],
                image=img_path,
                is_featured=d['is_featured'],
                is_new_arrival=d['is_new_arrival'],
                is_trending=d['is_trending'],
                is_active=True,
            )
            for tag_name in d['tags']:
                p.tags.add(tags[tag_name])
            products[d['name']] = p

        self.stdout.write('  Products done')

        # ─── VARIANTS + SIZES ───
        #
        # Structure:
        #   ProductVariant  → a named style, e.g. "Black", "Ivory", "EU 38"
        #   ProductVariantSize → a size within that style, e.g. S / M / L
        #
        # Ready-to-wear: two colourways (Black, Ivory), each with XS–XL
        # Footwear: one variant per EU size (no further size split)
        # Accessories / Jewellery: single "One Size" variant

        sku_counter = 1
        apparel_sizes = [('XS', 8), ('S', 10), ('M', 10), ('L', 8), ('XL', 5)]

        for product in Product.objects.filter(category__name='Ready to Wear'):
            sku_counter = make_variant(product, 'Black', apparel_sizes, sku_counter)
            sku_counter = make_variant(product, 'Ivory', apparel_sizes, sku_counter)

        for product in Product.objects.filter(category__name='Footwear'):
            for eu in ['36', '37', '38', '39', '40', '41']:
                # Each EU size is its own named variant with a single "One Size" size entry
                sku_counter = make_variant(
                    product,
                    f'EU {eu}',
                    [('One Size', 5)],
                    sku_counter,
                )

        for product in Product.objects.filter(category__name__in=['Accessories', 'Jewellery']):
            sku_counter = make_variant(
                product,
                'One Size',
                [('One Size', 8)],
                sku_counter,
            )

        self.stdout.write('  Variants done')

        # ─── PRODUCT DETAILS ───
        details_map = {
            'Le Manteau Croisé':    [('Material', '80% Wool, 20% Cashmere'), ('Lining', '100% Silk Satin'), ('Care', 'Dry clean only'), ('Origin', 'Made in Italy')],
            'La Robe Colonne':      [('Material', '100% Silk Crêpe'), ('Lining', '100% Silk'), ('Care', 'Dry clean only'), ('Origin', 'Made in France')],
            'Le Blazer Atelier':    [('Material', '100% Virgin Wool'), ('Lining', '100% Cupro'), ('Care', 'Dry clean only'), ('Origin', 'Made in Italy')],
            'Le Pantalon Tailleur': [('Material', '98% Wool, 2% Elastane'), ('Care', 'Dry clean only'), ('Origin', 'Made in Italy')],
            'Le Sac Voyage':        [('Material', 'Full-grain vegetable-tanned leather'), ('Hardware', 'Solid brass'), ('Lining', 'Cotton canvas'), ('Origin', 'Made in France')],
            'Le Portefeuille Long': [('Material', 'Smooth calfskin'), ('Slots', '12 card slots + coin pocket'), ('Origin', 'Made in France')],
            'Bague Soleil':         [('Metal', '18k Yellow Gold'), ('Stone', 'Pavé diamonds — 0.42ct'), ('Certificate', 'GIA certified'), ('Origin', 'Made in France')],
            'Collier Lune':         [('Metal', '18k White Gold'), ('Stone', 'Diamonds — 0.18ct'), ('Length', '42cm adjustable'), ('Origin', 'Made in France')],
            "L'Escarpin Signature": [('Material', 'Calfskin upper, leather sole'), ('Heel', '85mm'), ('Care', 'Use leather conditioner'), ('Origin', 'Made in Italy')],
            'La Mule Dorée':        [('Material', 'Metallic leather upper, suede lining'), ('Heel', 'Flat'), ('Origin', 'Made in Italy')],
        }
        for product_name, details in details_map.items():
            p = products.get(product_name)
            if p:
                for i, (title, value) in enumerate(details):
                    ProductDetail.objects.create(product=p, title=title, value=value, position=i)

        self.stdout.write('  Details done')

        # ─── DIMENSIONS ───
        for name, l, w, h, wt in [
            ('Le Sac Voyage',        50, 28, 22, 1.2),
            ('Le Portefeuille Long', 20,  2, 10, 0.1),
        ]:
            p = products.get(name)
            if p:
                ProductDimension.objects.create(
                    product=p, length_cm=l, width_cm=w, height_cm=h, weight_kg=wt
                )

        self.stdout.write('  Dimensions done')

        # ─── LOOKBOOKS ───
        LookBook.objects.all().delete()
        lookbook_data = [
            ('Wear the Silence',  'wear-the-silence', 'SS 2025 — A collection built on restraint.',         'SS 2025'),
            ("L'Heure Dorée",     'l-heure-doree',    'AW 2024 — Gold hour. When daylight turns to amber.', 'AW 2024'),
            ('La Nuit Étoilée',   'la-nuit-etoilee',  'Resort 2025 — Dressed for the night sky.',           'Resort 2025'),
        ]
        for title, slug, desc, season in lookbook_data:
            cover_path = copy_placeholder(placeholder, f'lookbooks/covers/{slug}.jpg')
            lb = LookBook.objects.create(
                title=title,
                slug=slug,
                description=desc,
                season=season,
                cover_image=cover_path,
                is_published=True,
            )
            for i in range(6):
                img_path = copy_placeholder(placeholder, f'lookbooks/{slug}-{i+1}.jpg')
                LookBookImage.objects.create(
                    lookbook=lb,
                    image=img_path,
                    caption=f'Look {i+1:02d}',
                    position=i,
                )

        self.stdout.write('  Lookbooks done')
        self.stdout.write(self.style.SUCCESS('Seed complete.'))

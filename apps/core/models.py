from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Announcement(models.Model):
    message    = models.CharField(max_length=255)
    link_text  = models.CharField(max_length=80, blank=True)
    link_url   = models.CharField(max_length=255, blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.message


class Category(models.Model):
    name  = models.CharField(max_length=100)
    slug  = models.SlugField(unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_list') + f'?category={self.slug}'


class Collection(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse(f'store:collection/{self.slug}/')


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):

    BADGE_CHOICES = [
        ('','— None —'),
        ('New','New'),
        ('SS 2025','SS 2025'),
        ('Limited','Limited'),
        ('Exclusive','Exclusive'),
        ('Sale','Sale'),
    ]

    # Core fields
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Image — replaces the JS-generated SVG art
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    # Badge shown on the card corner
    badge = models.CharField(max_length=20, choices=BADGE_CHOICES, blank=True)
    
    
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")

    # Homepage sections
    is_featured = models.BooleanField(default=False, help_text='Show in Icons of the Maison grid')
    is_new_arrival = models.BooleanField(default=False, help_text='Show in New Arrivals swiper')
    is_trending    = models.BooleanField(default=False, help_text='Show in Most Popular section')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.collection}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})


class ProductVariant(models.Model):
    SIZE_CHOICES = [
        ("XS", "XS"),
        ("S", "S"),
        ("M", "M"),
        ("L", "L"),
        ("XL", "XL"),
        ("XXL", "XXL"),
        ("One Size", "One Size"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50, blank=True, null=True)

    sku = models.CharField(max_length=100, unique=True)

    stock = models.PositiveIntegerField(default=0)

    price_override = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Leave empty to use product price"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("product", "size", "color")

    def __str__(self):
        return f"{self.product.name} ({self.size} - {self.color})"

    @property
    def final_price(self):
        return self.price_override if self.price_override else self.product.price


class ProductDimension(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="dimensions"
    )

    length_cm = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    width_cm = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    height_cm = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Dimensions for {self.product.name}"


class ProductDetail(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="details"
    )

    title = models.CharField(max_length=100)  # e.g Material, Care, Origin
    value = models.TextField()  # e.g 100% Cotton

    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.product.name} - {self.title}"
        

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="gallery"
    )

    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.product.name} Image"
        
        
class LookBook(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to="lookbooks/covers/", blank=True, null=True)
    season = models.CharField(max_length=100, blank=True, null=True)  # e.g Summer 2026
    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class LookBookImage(models.Model):
    lookbook = models.ForeignKey(
        LookBook,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="lookbooks/")
    caption = models.CharField(max_length=255, blank=True, null=True)
    position = models.PositiveIntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.lookbook.title} Image {self.id}"
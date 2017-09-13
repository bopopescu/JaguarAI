from functools import lru_cache

from decimal import Decimal
from django.db import models
from math import isnan


class BrowseNode(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    parent = models.PositiveIntegerField(null=True, blank=True)  # NOT an FK
    children = models.TextField(blank=True)  # A CSV of children IDs.
    name = models.CharField(max_length=256)
    full_name = models.CharField(max_length=1024, blank=True)
    follow = models.BooleanField(default=True)

    # cache these fields
    top_level_node = models.PositiveIntegerField(null=True, blank=True)

    @property
    def children_list(self):
        if not self.children:
            return []
        return [int(c) for c in self.children.split(',')]

    def __str__(self):
        return self.name


class Product(models.Model):
    # Primary fields
    asin = models.CharField(max_length=10, primary_key=True)
    last_updated_at = models.DateTimeField(null=True, blank=True)

    name = models.CharField(max_length=256)
    url = models.URLField()
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    review_count = models.IntegerField(blank=True, null=True)
    review_average = models.DecimalField(
        max_digits=2, decimal_places=1, blank=True, null=True)
    browse_nodes = models.ManyToManyField(BrowseNode, blank=True)

    # Secondary fields
    brand = models.CharField(max_length=256, blank=True)
    est_sales = models.IntegerField(
        blank=True, null=True, help_text="Predicted number of sales per month.")
    sales_rank = models.IntegerField(blank=True, null=True)
    number_sellers = models.IntegerField(blank=True, null=True)
    fba_fee = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    image_url = models.URLField(blank=True)
    seller = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f"{self.name[:24]} ${self.min_price}-${self.max_price} " \
               f"{self.review_average}★ {self.review_count}"

    @property
    def monthly_profit(self) -> float:
        """Calculate how much profit we should expect to be making if we sold
        a product like this.
        """
        # TODO: Add in estimated manufacturing costs
        sales = self.est_sales or 1
        fee = float(self.fba_fee or 0.0)
        price = float(self.min_price or 0.0)
        return sales * (price - fee)

    @property
    def unit_revenue(self) -> float:
        """Calculate how much profit we should expect to be making if we sold
        a product like this.
        """
        # TODO: Add in estimated manufacturing costs
        fee = float(self.fba_fee or 0.0)
        price = float(self.min_price or 0.0)
        return Decimal(price - fee)

    @property
    def is_space(self) -> bool:
        """The foothold is the ratio between how many reviews there are and
        how many units are sold per month. Old, established products should
        have a high foothold, while newer products should be low.
        """
        if self.review_average is None:
            return False
        if self.review_count < 10 or self.review_average < 2.5:
            return True
        # if self.review_foothold < 25.0 or self.review_average < 2.5:
        #     return True


class Search(models.Model):
    # Primary fields
    name = models.CharField(max_length=256)
    products = models.ManyToManyField(Product, blank=True)
    completed = models.BooleanField(default=False)
    browse_node = models.ForeignKey(BrowseNode, null=True, blank=True)
    last_updated_at = models.DateTimeField(null=True, blank=True)

    # Cached, calculated fields
    avg_volume = models.FloatField(default=0)
    avg_review_count = models.FloatField(default=0)
    avg_review_score = models.FloatField(default=0)
    avg_price = models.FloatField(default=0)
    min_price = models.FloatField(default=0)
    max_price = models.FloatField(default=0)
    avg_revenue = models.FloatField(default=0)
    max_revenue = models.FloatField(default=0)
    trend = models.CharField(max_length=16, choices=(
        ('upward', 'upward'),
        ('downward', 'downward'),
        ('stable', 'stable'),
        ('seasonal', 'seasonal'),
        ('unknown', 'unknown'),
    ), default='unknown')
    seller_diversity = models.FloatField(default=0)
    accessory_percentage = models.FloatField(default=0)

    def __str__(self):
        return f"{self.name}"

    @property
    @lru_cache(1)
    def product_cache(self):
        """Cache this for fast computing."""
        return list(self.products.all())

    def calculate(self, op, attr):
        """Safely calculate statistical functions on product properties."""
        data = [getattr(p, attr) for p in self.product_cache
                if getattr(p, attr) is not None and not isnan(getattr(p, attr))]
        if not data:
            return 0
        val = round(op(data), 2)
        if val is None:
            print(op, attr, self)
        return val or 0

    class Meta:
        verbose_name_plural = "Searches"
        ordering = ("-avg_volume", )


class FavoriteProduct(models.Model):
    user = models.ForeignKey('users.JaguarUser')
    product = models.ForeignKey(Product)
    unit_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="The unit cost you can acquire this product for.")

    def __str__(self):
        return f'{self.user} {self.product}'

    class Meta:
        unique_together = (('user', 'product'), )


class SavedSearch(models.Model):
    user = models.ForeignKey('users.JaguarUser')
    name = models.CharField(max_length=64, blank=True)
    param_string = models.CharField(max_length=1024)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} {self.name}'

    def annotate_query_params(self):
        pairs = self.param_string.strip('&').split('&')
        self.params = {pair.split('=')[0]: pair.split('=')[1] for pair in pairs}

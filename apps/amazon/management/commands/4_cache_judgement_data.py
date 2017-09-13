"""
"""
from statistics import median_grouped, mode, StatisticsError

from django.core.management.base import BaseCommand
from django.db.transaction import atomic
from tqdm import tqdm

from apps.amazon.models import Search


class Command(BaseCommand):
    help = "Run network requests to create search and product data."

    def handle(self, *args, **kwargs):
        with atomic():
            # TODO: Search.objects.filter(fba_fee=float('nan')) -> zeros?

            for search in tqdm(Search.objects.all()):
                # Setup convenient shortcuts
                c = search.calculate

                # First page space
                search.avg_volume = c(median_grouped, 'est_sales')
                search.avg_review_score = c(median_grouped, 'review_average')
                search.avg_review_count = c(median_grouped, 'review_count')
                search.avg_price = c(median_grouped, 'min_price')
                search.avg_revenue = c(median_grouped, 'monthly_profit')
                search.max_revenue = c(max, 'monthly_profit')
                search.total_revenue = c(sum, 'monthly_profit')

                # Save it all
                search.save()

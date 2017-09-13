"""Hit Amazon's store pages to get product lists for each search.
"""
import asyncio
import json
from datetime import timedelta
from statistics import median_grouped

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.db.transaction import atomic
from django.utils.timezone import now
from tqdm import tqdm

from apps.amazon.management.commands._network2 import AnonymousClient
from apps.amazon.models import Search, BrowseNode, Product
from apps.amazon.management.commands import _amazon


queue = asyncio.Semaphore(2)  # Only run two in parallel


class Command(BaseCommand):
    help = "Run network requests to create search and product data."

    def handle(self, *args, **kwargs):
        self.make_searches_for_all_browse_nodes()

        # Run a preliminary query on Amazon for this search
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_searches())
        loop.close()

    def make_searches_for_all_browse_nodes(self):
        with atomic():
            # Create a Search for each BrowseNode
            for n in BrowseNode.objects.annotate(
                count=Count('search')
            ).filter(count=0):
                print(n.full_name.encode('ascii', 'ignore'))
                new = Search(name=n.name, browse_node=n, )
                new.save()

    async def get_searches(self):
        client = AnonymousClient()

        outstanding_searches = Search.objects.filter(
            Q(last_updated_at__isnull=True) |  # Never been run
            Q(last_updated_at__lte=now() - timedelta(days=14))  # Older than 2wk
        )
        tasks = [self.get_search(client, s) for s in outstanding_searches]
        self.pbar = tqdm(asyncio.as_completed(tasks), total=len(tasks))
        for f in self.pbar:
            self.pbar.set_postfix(ip=client.last_ip_address)
            await f

        client.cleanup()

    async def get_search(self, client, search):
        async with queue:
            products = await _amazon.get_products_from_browse_node_page(
                client, search.browse_node_id)

            # Update products
            tasks = [self.update_product(client, p) for p in products]
            await asyncio.gather(*tasks)
            search.products = products

            # Cache the judgement data
            self.cache_data(search)

            # Save it all
            search.save()

    async def update_product(self, client, p: Product):
        age = now() - p.last_updated_at if p.last_updated_at else timedelta(days=99)
        if age < timedelta(days=14):
            return  # It's pretty fresh, so skip

        try:
            response = await client.get(f'https://amzscout.net/api/v1/landing/fees?asin={p.asin}&domain=COM')
            data = json.loads(response)

            fees = data.get('fees', {}) or {}
            p.fba_fee = fees.get('total', -1)
            p.est_sales = data['product'].get('estSales', -1)
            p.last_updated_at = now()
            p.save()
        except Exception as e:
            print("Failed to get the product", p.asin, e)

    def cache_data(self, search):
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
        search.last_updated_at = now()

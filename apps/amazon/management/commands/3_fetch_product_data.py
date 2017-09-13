"""
"""
import asyncio
import json

from django.core.management.base import BaseCommand
from tqdm import tqdm

from apps.amazon.management.commands._network2 import AnonymousClient
from apps.amazon.models import Product


class Command(BaseCommand):
    help = "Run network requests to create search and product data."

    def handle(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.fetch_products())

    async def fetch_products(self):
        client = AnonymousClient()
        # Use external services to fill in the product details
        print("Getting Product List (this query can take a really long time)")
        products = list(Product.objects.filter(est_sales=None))
        tasks = [self.update_product(client, p) for p in products]
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            await f

        client.cleanup()

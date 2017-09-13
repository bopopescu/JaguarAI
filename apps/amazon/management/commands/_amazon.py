import random
import re
import time
from typing import List, Optional
from urllib.error import HTTPError

import bs4
from amazon.api import AmazonAPI

from apps.amazon.management.commands._network2 import AnonymousClient
from apps.amazon.models import BrowseNode
from apps.amazon.models import Product

TIMEOUTS = {
    'amazon_api': 4,
}
AMZ_ACCESS_KEY = 'AKIAIGHLJTJRTXL7ENIQ'
AMZ_SECRET_KEY = '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'
AMZ_ASSOC_TAG = 'brimhall-20'
AMAZON = AmazonAPI(AMZ_ACCESS_KEY, AMZ_SECRET_KEY, AMZ_ASSOC_TAG)


def products_from_soup(soup: bs4.Tag) -> Optional[Product]:
    # Get name & link
    name_tag = soup.find('a', {'class': 's-access-detail-page'})
    if name_tag:
        name = name_tag.get('title')
        url = name_tag.get('href')
    else:
        return None

    # Get the asin
    try:
        url_parts = url.split('/')
        dp = url_parts.index('dp')
        asin = url_parts[dp+1]
    except ValueError:
        return None

    # Get price
    def parse_price(s: str) -> float:
        return float(
            s.replace('Suggested Retail Price: ', '')
             .replace(',', '')
             .replace('$', '')
             .strip())
    price_tag = soup.find('span', {'aria-label': re.compile('\$[0-9.]')})
    price_str = price_tag.get('aria-label') if price_tag else '0'
    prices = [parse_price(s) for s in price_str.split('-')]
    min_price = prices[0]
    if len(prices) == 1:
        max_price = min_price
    else:
        max_price = prices[1]

    # Get ratings
    star_tag = soup.find('i', {'class': 'a-icon-star'})
    if star_tag:
        review_average_tag = star_tag.find('span', {'class': 'a-icon-alt'})
        avg_str = review_average_tag.contents[0]
        avg_str = avg_str.replace(' out of 5 stars', '')
        review_average = float(avg_str)
    else:
        review_average = 0

    count_tag = soup.find('a', {"href": re.compile('customerReviews')})
    if count_tag:
        review_count = int(count_tag.contents[0].replace(',', ''))
    else:
        review_count = 0

    # Get the product image
    try:
        image_tag = soup.find('img', {'alt': 'Product Details'})
        image_url = image_tag.get('src')
    except AttributeError:
        image_url = ""

    # Get the brand (this is a touch fragile)
    try:
        brand = soup.find_all('span', {'class': 'a-size-small'})[1].text
    except IndexError:
        brand = ''

    # Later: Get the sales rank (if we want to use Unicorn Smasher)
    # Later: Get number of sellers - look for the link with "(9 New Offers)"

    product, created = Product.objects.get_or_create(
        asin=asin,
        defaults=dict(
            name=name,
            url=url,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            review_count=review_count,
            review_average=review_average,
            image_url=image_url,
        )
    )
    product.save()
    return product


async def get_products_from_browse_node_page(client: AnonymousClient, node_id: int) -> List[Product]:
    url = 'https://www.amazon.com/All/b/'
    params = {
        "ie": "UTF8",
        "node": node_id,
    }

    # Go to amazon
    response = None
    while response is None:
        try:
            response = await client.get(url, params=params)
        except Exception as e:
            print(e, "Failed to get the HTML, retrying in 30s")
            time.sleep(30)
    soup = bs4.BeautifulSoup(response, 'html.parser')

    # Parse the response
    products = []
    results = soup.find_all('li', {'class': 's-result-item'})
    for result in results:
        p = products_from_soup(result)
        if p is not None:
            products.append(p)

    return products


#############################################################################


FOLLOW_BLACKLIST = [
    "Featured Categories",
    "Specialty Stores",
    "Self-Service",
]


def find_browse_node(seed=None, parent_name: str=''):
    # Check our database first
    try:
        return BrowseNode.objects.get(id=seed)
    except BrowseNode.DoesNotExist:
        pass

    # Run the request until it works
    nodes = None
    while nodes is None:
        try:
            # Wait a random amount of time
            tts = TIMEOUTS['amazon_api'] + random.uniform(0, 0.5)
            print("              Query", tts)
            time.sleep(tts)
            nodes = AMAZON.browse_node_lookup(BrowseNodeId=seed)
        except HTTPError:
            # Add 1 second to the timeout
            TIMEOUTS['amazon_api'] += 1
            print("Timeout. Waiting 30 seconds and resuming at a slower pace")
            time.sleep(30)
        except AttributeError as e:
            # The browse node doesn't exist
            b = BrowseNode(
                id=seed,
                name="UNKNOWN",
                full_name="UNKNOWN",
                parent=None,
                children=[],
                follow=False
            )
            b.save()
            return b

    # Record the data
    for result in nodes:
        try:
            parent_id = result.ancestor.id
        except AttributeError:
            parent_id = None
        full = f"{parent_name} > {result.name}" if parent_name else result.name
        try:
            child_ids = ",".join([str(c.id) for c in result.children])
        except AttributeError:
            child_ids = ""
        b = BrowseNode(
            id=result.id,
            name=result.name,
            full_name=full,
            parent=parent_id,
            children=child_ids,
            follow=result.name not in FOLLOW_BLACKLIST
        )
        b.save()
    return b


# TODO: After this scan runs, find all missing parents and do it all again.
# TODO: Then rewrite the hierarchy

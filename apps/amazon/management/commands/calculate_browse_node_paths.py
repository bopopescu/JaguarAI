"""
"""
from collections import deque

from django.core.management.base import BaseCommand
from django.db.transaction import atomic
from tqdm import tqdm

from apps.amazon.management.commands.fetch_browse_nodes import \
    TOP_LEVEL_BROWSE_NODES
from apps.amazon.models import BrowseNode
from ._amazon import find_browse_node


class Command(BaseCommand):
    help = "Run a breadth-first search of amazon categories."

    def handle(self, *args, **kwargs):
        with atomic():
            nodes = {n.id: n for n in BrowseNode.objects.all()}
            for node in tqdm(nodes.values()):
                # Rebuild the full name
                if node.id in TOP_LEVEL_BROWSE_NODES:
                    node.top_level_node = node.id
                    node.save()
                    continue
                cursor = node
                while node.top_level_node is None:
                    parent = nodes.get(cursor.parent)
                    if not parent:
                        node.top_level_node = cursor.id
                        node.save()
                        break
                    cursor = parent

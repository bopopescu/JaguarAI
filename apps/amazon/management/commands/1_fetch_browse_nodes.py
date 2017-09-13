"""
"""
from collections import deque

from django.core.management.base import BaseCommand

from ._amazon import find_browse_node


TOP_LEVEL_BROWSE_NODES = [
    2350149011, 2617941011, 15684181, 165796011, 3760911,
    384082011, 283155, 502394, 2335753011, 468642, 541966,
    172282, 16310211, 3760901, 1055398, 16310161, 133140011,
    284507, 599858, 2625373011, 5174, 11091801, 1064954,
    2619533011, 229534, 3375251, 228013, 165793011,
]
# Bad nodes = 1036592, 10963061, 3367581, 2334092011, 672123011, 1267877011


# HEADS UP! This might be a faster way to get these:
# https://www.amazon.com/exec/obidos/tg/browse/-/{browse_node_id}
# The bbn param on the links in the sidebar is the current page's browse node
# So you might have to click into the page to get the active browse node?

# ALSO: you might want to look at this for fetching ASIN data:
# https://www.amazon.com/exec/obidos/ASIN/0521810086


class Command(BaseCommand):
    help = "Run a breadth-first search of amazon categories."

    def handle(self, *args, **kwargs):
        # Initialize
        nodes = [find_browse_node(seed=s) for s in TOP_LEVEL_BROWSE_NODES]
        nodes = [n for n in nodes if n.follow]
        queue = deque()
        queue.extend(nodes)

        while queue:
            node = queue.popleft()

            # Then downward
            for seed in node.children_list:
                child = find_browse_node(seed=seed, parent_name=node.full_name)
                print(f"{child.full_name}", len(queue))
                if child.follow:
                    queue.append(child)

        # Find any nodes that are missing (inefficiently)
        # for n in tqdm(BrowseNode.objects.all()):
        #     try:
        #         if n.parent and not BrowseNode.objects.filter(id=n.parent).exists():
        #             print("Fetching new", n.parent)
        #             find_browse_node(seed=n.parent)
        #     except:
        #         print("Nope")

        # TODO: Fix all full_names

        # Beep when done
        #import os
        #os.system('play --no-show-progress --null --channels 1 synth 1 sine 1000')
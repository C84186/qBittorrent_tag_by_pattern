#!/bin/python

import helpers, defs

import qbittorrentapi
import re, logging
from pathlib import Path

_L = logging.getLogger(__name__)

credentials_path = defs.credentials_path

category_defs = defs.tag_category

set_prefix = category_defs['set_prefix']
get_prefix = category_defs['get_prefix']
uncat_kw   = category_defs['uncat']

dry_run = False
# Let's define the behaviour

"""
For each category, 2 tags are used for synchronization
They are given special prefixes to distinguish them from a normal tag

_CAT_{category_name} :

   * "Get" tag
   * Read-Only
   * This reflects the current category state of the torrent.
   * It should be considered read-only, as it is automatically updated
     by the category state of a torrent.

_SET_{category_name} :

   * "Set" / "Intent" tag
   * This signals the intent to categorize the torrent

Special suffix:

    "" (Empty string):
    * Corresponds to "_SET_", "_CAT_"
    * Reflects torrents with no category
"""

"""
Firstly, process intent tags (eg: "_SET_cat1"_

When you find an intent tag:
- assign it the correct cat ( category: cat1 )
- If the category is the uncategorized keyword ( _UNCAT ), remove the category
- remove the intent tag, and any other associated intent tag
- We could now update the reflect tag, but we won't, 
  - the reflect tag will be given purely from the category state
    of the torrent.
"""
def process_sets(qbt : qbittorrentapi.Client):
    L = logging.getLogger(_L.name + '.set')
    existing_cats = qbt.torrent_categories.categories.keys()
    existing_tags = qbt.torrent_tags.tags

    sub_pat   = f"^{set_prefix}"
    match_pat = f"^{set_prefix}.*"

    # Find every tag with the prefix, and relate it to its category
    setter_tags = { re.sub(sub_pat, "", tag) : tag for tag in existing_tags if re.match(match_pat, tag) }

    # No need to remove unsetter_tag from setter_tags as we break early for special case
    unsetter_tag = set_prefix + uncat_kw

    L.info(f"looking for tags in {setter_tags}")
    L.info("Fetching torrents")

    max_retries = 5

    torrent_list = helpers.retry_method(qbt.torrents.info, max_retries, L)

    for t in torrent_list:
        torrent_tags = { tag.strip() for tag in t.tags.split(',') }

        # break early for special case
        if unsetter_tag in torrent_tags:
            L.info(f"{t.name} : Found {unsetter_tag}, removing cat")
            if not dry_run:
                if setter_tags.values(): t.remove_tags(setter_tags.values())
                t.set_category(category = None)
            continue

        for cat, tag in setter_tags.items():

            if tag in torrent_tags:
                L.info(f"{t.name} : Found {tag}, assigning {cat}")
                L.info(f"{t.name} : Removing {setter_tags.values()}")
                if not dry_run:
                    if setter_tags.values(): t.remove_tags(setter_tags.values())
                    # what if category doesnt exist yet? I dont know if this errors, 
                    # or just makes the category
                    t.set_category(category = cat)
                break


"""
Now, process "get/reflect" tags (eg: "_CAT_cat1" )

For each torrent, check if it has "_CAT_*".
If it has _CAT_{kw} where kw != the torrent's category, remove that tag.
Add _CAT_{category}
"""
def process_gets(qbt: qbittorrentapi.Client):
    L = logging.getLogger(_L.name + '.get')
    existing_cats = qbt.torrent_categories.categories

    # The empty category
    existing_cats["uncategorized"] = {"name" : uncat_kw}

    match_pat = f"^{get_prefix}.*"
    for key in existing_cats:
        cat = existing_cats[key]['name']
        L.info(f"cat:{key}:processing get tags for '{cat}'")

        torrent_list = qbt.torrents.info(category = cat)

        correct_tag = get_prefix + cat

        for t in torrent_list:
            torrent_tags = [ tag.strip() for tag in t.tags.split(',') ]

            tags_to_rm =  [ tag for tag in torrent_tags if re.match(match_pat, tag) and not tag == correct_tag ]

            if tags_to_rm:
                L.info(f"cat:{key}:{t.name}: Removing {tags_to_rm}")
                if not dry_run: t.remove_tags(tags_to_rm)

            if not correct_tag in torrent_tags:
                L.info(f"cat:{key}:{t.name}: Adding {correct_tag}")
                if not dry_run: t.add_tags([correct_tag])

def process_all(qbt: qbittorrentapi.Client):
    process_sets(qbt)
    process_gets(qbt)

def main():
    logging.basicConfig(level = logging.INFO)
    qbt = helpers.connect_client()
    process_all(qbt)

if __name__ == "__main__":
    _L = logging.getLogger()
    main()

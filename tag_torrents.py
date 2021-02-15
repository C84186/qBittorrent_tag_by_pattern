import helpers, defs

import qbittorrentapi
import json, yaml, re
from pathlib import Path

tag_hashes = {}

dry_run = True 

credentials_path = defs.credentials_path
tag_for_invalid_overlap = defs.tag_for_invalid_overlap

uncat_kw = defs.uncategorized_kw

qbt_client = helpers.connect_client(credentials_path)

with open('tags.yml') as f:
    tag_map = yaml.load(f)


exclusive_labels = set()
if 'flag_confused_if_together' in tag_map: exclusive_labels = set(tag_map['flag_confused_if_together'])

category = None
if 'category' in tag_map:
    if tag_map['category'] != '*':
        category = tag_map['category']



# display qBittorrent info
print(f'qBittorrent: {qbt_client.app.version}')
print(f'qBittorrent Web API: {qbt_client.app.web_api_version}')
for k,v in qbt_client.app.build_info.items(): print(f'{k}: {v}')

untagged_hashes = set()

all_torrents =  qbt_client.torrents_info()
# retrieve and show all torrents
for torrent in all_torrents:

    print(f"processing: {torrent.name}")
    current = {}

    current['torrent'] = torrent#{'name' : torrent.name, 'hash' : torrent.hash}

    current['files'] = list(qbt_client.torrents_files(torrent.hash))
    # https://qbittorrent-api.readthedocs.io/en/latest/apidoc/torrents.html#qbittorrentapi.torrents.TorrentsAPIMixIn.torrents_create_tags
    # https://qbittorrent-api.readthedocs.io/en/latest/apidoc/torrents.html#qbittorrentapi.torrents.TorrentDictionary.add_tags

    current_tags = set()
    
    print(torrent['category'])

    process_torrent = True
    if category:
        if category == uncat_kw:
            if not 'category' in torrent or not torrent['category']: process_torrent = True
            elif torrent['category'] == category: process_torrent = True

    if process_torrent:
        for label in tag_map['labels']:
            print(f" - processing {label['name']}")
            if 'extension' in label and label['extension']:
                print(f"  - processing extensions for {label['name']}")
                
                matched_extension = False
                for ext in label['extension']:
                    ext = f".{ext}".lower()

                    for path in current['files']:
                        path = path['name']
                        path = Path(path)
                        if path.suffix.lower() == ext:
                            print(f"    - found '{ext}' in {path.name}")
                            current_tags.add(label['name'])

                            matched_extension = True


                            if not label['name'] in tag_hashes:
                                tag_hashes[label['name']] = set()

                            tag_hashes[label['name']].add(torrent['hash'])

            if 'regex' in label and label['regex']:
                print(f"  - processing regex for {label['name']}")

                for re_pat in label['regex']:
                    m = re.fullmatch(re_pat, torrent['name'])

                    if m:
                        print(f"    - found match for regex: '{re_pat}'")
                        current_tags.add(label['name'])

                        if not label['name'] in tag_hashes:
                            tag_hashes[label['name']] = set()

                        tag_hashes[label['name']].add(torrent['hash'])

    exclusive_overlap = exclusive_labels.intersection(current_tags)
    print(current_tags)
    print(exclusive_labels)
    print(exclusive_overlap)
    if len(exclusive_overlap) > 1:
        print(f" - {torrent['name']} matches too many tags: {exclusive_overlap}")

        current_tags.add(tag_for_invalid_overlap)

    current['new_tags'] = list(current_tags)

    print(f" - new tags: {current_tags}")

    if not dry_run and len(current_tags):
        existing_tags = set(torrent['tags'])

        if current_tags != existing_tags:
            torrent.add_tags(list(current_tags))

    if not len(current_tags):
        paths = [Path(x['name']).name for x in current['files']]

        print(f"NO_TAG_NAME: {torrent.name}")
        print(f"NO_TAG_FILES: files: {paths}")
        print(f"NO_TAG_HASH: {torrent['hash']}")

        untagged_hashes.add(torrent['hash'])


    #  print(json.dumps(current, sort_keys=True, indent=4))

#  for tag in tag_hashes:
#      print(f"Number of torrents for {tag}: {len(tag_hashes[tag])}")
#
#      if not dry_run: qbt_client.torrents_add_tags(tags = tag, torrent_hashes = list(tag_hashes[tag]))
#
#  print(f"Number of untagged torrents: {len(untagged_hashes)}")
#
#  print(f"Number of torrents: {len(all_torrents)}")
import helpers, defs

import qbittorrentapi
import json, yaml, re
from pathlib import Path


dry_run = False

credentials_path = defs.credentials_path
tag_for_invalid_overlap = defs.tag_for_invalid_overlap

uncat_kw = defs.uncategorized_kw


with open('tags.yml') as f:
    tag_map = yaml.load(f)


exclusive_labels = set()
if 'flag_confused_if_together' in tag_map: exclusive_labels = set(tag_map['flag_confused_if_together'])

category = None
if 'category' in tag_map:
    if tag_map['category'] != '*':
        category = tag_map['category']


def tag_torrents(torrent_list, qbt_client):
    # display qBittorrent info
    print(f'qBittorrent: {qbt_client.app.version}')
    print(f'qBittorrent Web API: {qbt_client.app.web_api_version}')
    for k,v in qbt_client.app.build_info.items(): print(f'{k}: {v}')

    tag_hashes = {}
    untagged_hashes = set()
    skipped_hashes = set()

    # retrieve and show all torrents
    for torrent in torrent_list:

        print(f"processing: {torrent.name}")
        current = {}

        current['torrent'] = torrent#{'name' : torrent.name, 'hash' : torrent.hash}

        current['files'] = list(qbt_client.torrents_files(torrent.hash))
        # https://qbittorrent-api.readthedocs.io/en/latest/apidoc/torrents.html#qbittorrentapi.torrents.TorrentsAPIMixIn.torrents_create_tags
        # https://qbittorrent-api.readthedocs.io/en/latest/apidoc/torrents.html#qbittorrentapi.torrents.TorrentDictionary.add_tags

        current_tags = set()
        
        print(f" category: {torrent['category']}")

        process_torrent = False
        if not category:
            process_torrent = True
        else:
            if category == uncat_kw:
                if not 'category' in torrent or not torrent['category']: process_torrent = True
            elif torrent['category'] == category: process_torrent = True

        if not process_torrent:
            print(f" - skipping as {torrent['category']} != {category}")
            skipped_hashes.add(torrent['hash'])
            continue
        
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

    print(f"Number of untagged torrents: {len(untagged_hashes)}")
    print(f"Number of skipped torrents: {len(skipped_hashes)}")
    print(f"Number of torrents: {len(torrent_list)}")
    return untagged_hashes, skipped_hashes

if __name__ == "__main__":
    qbt_client = helpers.connect_client(credentials_path)
    all_torrents =  qbt_client.torrents_info()
    untagged_hashes, skipped_hashes = tag_torrents(all_torrents, qbt_client) 

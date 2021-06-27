import helpers, defs

import qbittorrentapi
import logging
L = logging.getLogger(__name__)

credentials_path = defs.credentials_path

def add_tracker_list_single(torrent : qbittorrentapi.torrents.TorrentDictionary, tracker_list: list):
    torrent_trackers = torrent.trackers
    
    torrent_trackers = [tracker["url"] for tracker in torrent_trackers if "url" in tracker]

    remove_trackers = False
    placeholder_idx = -1
    remove_trackers =  defs.placeholder_tracker in torrent_trackers

    if remove_trackers:
        placeholder_idx = torrent_trackers.index(defs.placeholder_tracker)

        L.info(f"{torrent.name}: Found placeholder at {placeholder_idx}")
        # remove everything after placeholder (if not found, remove nothing)
        # get a list of urls
        to_rm = tracker_list[placeholder_idx:-1]
        to_rm = [tracker["url"] for tracker in to_rm if "url" in tracker]

        to_rm = [defs.placeholder_tracker] + to_rm

        torrent.remove_trackers(urls = to_rm)

    # Now can readd trackers
    tracker_list = [defs.placeholder_tracker] + tracker_list
    torrent.add_trackers(urls = tracker_list)


def add_tracker_list(torrent_hashes, qbt_client, tracker_list):
    torrents = qbt_client.torrents.info(torrent_hashes = torrent_hashes)

    for torrent in torrents:
        add_tracker_list_single(torrent, tracker_list)




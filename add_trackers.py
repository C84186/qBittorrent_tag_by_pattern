import helpers, defs
import logging, typing

import qbittorrentapi

from qbittorrentapi.torrents import TorrentInfoList, TorrentDictionary

dry_run = True

TorrentList_t = typing.Union[typing.List[TorrentDictionary], TorrentInfoList]
L = logging.getLogger(__name__)

credentials_path = defs.credentials_path

def add_tracker_list_single(torrent : TorrentDictionary, tracker_list: typing.List[str]):
    torrent_trackers = torrent.trackers
    
    torrent_trackers = [tracker["url"] for tracker in torrent_trackers if "url" in tracker]
    to_add = [tracker for tracker in tracker_list if not tracker in torrent_trackers]

    L.info(f"Adding {len(to_add)} trackers for {torrent.name}")
    
    torrent_tags = { tag.strip() for tag in torrent.tags.split(',') }

    # Add trackers & tag the torrent 
    if not dry_run:

        if to_add:
            torrent.add_trackers(urls = to_add)
            torrent.reannounce()

        if not defs.tag_tracker_managed in torrent_tags:
            L.info(f"Adding {defs.tag_tracker_managed} to {torrent.name}")
            torrent.add_tags([defs.tag_tracker_managed])

def add_tracker_list(torrents : TorrentList_t, tracker_list : typing.List[str]):
    L.info(f"Processing list of {len(torrents)}")
    for torrent in torrents:
        add_tracker_list_single(torrent, tracker_list)


def read_tracker_list(path : defs.pathlike_hint = "./trackerslist/trackers_best.txt"):
    out = []
    with open(path) as f:
        out = f.readlines()

    return out

def find_trackerless(torrents : TorrentList_t):
    out = []
    for torrent in torrents:
        torrent_trackers = [t["url"] for t in torrent.trackers if "url" in t]
        is_trackerless = all(url in defs.builtin_trackers for url in torrent_trackers)

        if is_trackerless: out.append(torrent)
    return out

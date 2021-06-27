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

    remove_trackers = False
    placeholder_idx = -1
    remove_trackers =  defs.placeholder_tracker in torrent_trackers

    if remove_trackers:
        placeholder_idx = torrent_trackers.index(defs.placeholder_tracker)

        L.info(f"{torrent.name}: Found placeholder at {placeholder_idx} of {len(torrent_trackers)}")
        # remove everything after placeholder (if not found, remove nothing)
        # get a list of urls
        to_rm = tracker_list[placeholder_idx:-1]
        L.info(f"Removing {len(to_rm)}:  {to_rm}")
        to_rm = [tracker["url"] for tracker in to_rm if "url" in tracker]

        to_rm = [defs.placeholder_tracker] + to_rm

        if not dry_run:
            torrent.remove_trackers(urls = to_rm)

    # Now can readd trackers
    tracker_list = [defs.placeholder_tracker] + tracker_list
    
    if not dry_run:
        torrent.add_trackers(urls = tracker_list)
        torrent.reannounce()


def add_tracker_list(torrents : TorrentList_t, tracker_list : typing.List[str]):
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

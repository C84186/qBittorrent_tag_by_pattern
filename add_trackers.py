import helpers, defs
import logging, typing

import qbittorrentapi

from qbittorrentapi.torrents import TorrentInfoList, TorrentDictionary

dry_run = False 

TorrentList_t = typing.Union[typing.List[TorrentDictionary], TorrentInfoList]
L = logging.getLogger(__name__)

credentials_path = defs.credentials_path

def add_tracker_list_single(torrent : TorrentDictionary, tracker_list: typing.List[str]):
    torrent_trackers = torrent.trackers
    
    torrent_trackers = [tracker["url"] for tracker in torrent_trackers if "url" in tracker]
    to_add = [tracker for tracker in tracker_list if not tracker in torrent_trackers]

    L.info(f"Adding {len(to_add)} trackers for {torrent.name}")

    # Add trackers & tag the torrent 
    if not dry_run:

        if to_add:
            torrent.add_trackers(urls = to_add)
            torrent.reannounce()


def add_tracker_list(torrents : TorrentList_t, tracker_list : typing.List[str]):
    L.info(f"Processing list of {len(torrents)}")
    for torrent in torrents:
        add_tracker_list_single(torrent, tracker_list)


def read_tracker_list(path : defs.pathlike_hint = "./trackerslist/trackers_best.txt"):
    out = []
    with open(path) as f:
        out = f.readlines()

    out = [line.strip() for line in out if line.strip()]
    L.info(out)
    return out

def find_trackerless(torrents : TorrentList_t):
    out = []
    for torrent in torrents:
        torrent_trackers = [t["url"] for t in torrent.trackers if "url" in t]
        is_trackerless = all(url in defs.builtin_trackers for url in torrent_trackers)

        if is_trackerless: out.append(torrent)
    return out


def main():
    logging.basicConfig(level = logging.INFO)
    qbt = helpers.connect_client() 

    all_torrents = qbt.torrents_info()
    tagged_torrents = helpers.filter_for_tags(all_torrents, has_tags = [defs.tag_tracker_managed])

    L.info(f"Number of torrents to process: {len(tagged_torrents)}")

    tracker_list = read_tracker_list()

    add_tracker_list(tagged_torrents, tracker_list)

if __name__ == "__main__":
    main()

import helpers, defs
import logging, typing, time
from pathlib import Path

import requests as rq
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

    if len(to_add):
        L.info(f"Addin:g {len(to_add)} trackers for {torrent.name}")

    # Add trackers & tag the torrent 
    if not dry_run:

        if to_add:
            torrent.add_trackers(urls = to_add)
            torrent.reannounce()


def add_tracker_list(torrents : TorrentList_t, tracker_list : typing.List[str]):
    L.info(f"Processing list of {len(torrents)}")
    for torrent in torrents:
        add_tracker_list_single(torrent, tracker_list)

def save_tracker_list(path: defs.pathlike_hint):
    data = rq.get('https://cdn.jsdelivr.net/gh/ngosang/trackerslist@master/trackers_best.txt')
    with open(path, 'w') as f:
        f.write(data.text)

def should_download_tracker_file(path: defs.pathlike_hint): 
    path = Path(path)
    
    file_exists = path.is_file()

    if not file_exists:
        L.info("Tracker file not found, downloading!")
        return True

    file_mtime = path.stat().st_mtime
    current_time = time.time()

    file_hours = (current_time - file_mtime) / 3600
    
    file_older_than_day = file_hours >= 24

    if file_older_than_day:
        L.info(f"Tracker file is {file_hours} old, download!")

    return file_older_than_day

def read_tracker_list(path : defs.pathlike_hint = "/app/trackerslist/trackers_best.txt"):



    should_download = should_download_tracker_file(path) 

    if should_download:
        save_tracker_list(path)

    
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

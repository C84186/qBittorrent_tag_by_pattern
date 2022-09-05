import helpers, defs, paths, tag_torrents
from defs import pathlike_hint

import qbittorrentapi, yaml, progressbar
from functools import partial
import pathlib, logging, itertools, os

L = logging.getLogger(__name__)
logging.basicConfig(level = logging.WARNING)
path_specs = paths.read_path_spec()
credentials_path = defs.credentials_path
bt_backup_p = paths.get_bt_backup_path()

def find_empty_fastresumes(bt_backup_p : pathlike_hint = bt_backup_p) -> list:
    """
    Get torrent files that correspond to empty fastresumes
    """
    bt_backup_p = pathlib.Path(bt_backup_p)

    out = []

    for fastresume_path in bt_backup_p.iterdir():
        if fastresume_path.suffix != ".fastresume": continue 
        if fastresume_path.stat().st_size == 0:
            L.info(f"Empty fastresume at {fastresume_path}")
            torrent_path = fastresume_path.with_suffix(".torrent")
            if torrent_path.exists() and torrent_path.stat().st_size != 0: out.append(torrent_path)
    return out

def add_torrents_to_client(torrents_with_broken_frs : list, qbt_client : qbittorrentapi.client.Client) -> list:
    """
    Do this paused
    """
    to_restore_tag = "TO_RESTORE"
    qbt_client.torrents_create_tags(tags = [to_restore_tag])

    # Add in chunks to avoid opening too many files at once
    for chunk in helpers.chunks(torrents_with_broken_frs, 1000):
        if True: 
            qbt_client.torrents.add(torrent_files = chunk, tags = [to_restore_tag], is_paused = True)

        chunk_hashes = [torrent_path.stem for torrent_path in chunk]
        qbt_client.torrent_tags.add_tags(tags = to_restore_tag, torrent_hashes = chunk_hashes)

    new_hashes = [torrent_path.stem for torrent_path in torrents_with_broken_frs]
    
    new_torrents = qbt_client.torrents_info(torrent_hashes = new_hashes)
    # TODO: Get proper type hint
    # tag_torrents.tag_torrents(new_torrents, qbt_client)
    return new_torrents

if __name__ == "__main__":
    qbt_client = helpers.connect_client(credentials_path)
    torrents_to_restore = find_empty_fastresumes()
    add_torrents_to_client(torrents_to_restore, qbt_client)

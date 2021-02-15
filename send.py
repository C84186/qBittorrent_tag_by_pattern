import helpers, defs, paths, fastresume, ssh

import qbittorrentapi, yaml, progressbar
import pathlib, logging, itertools

L = logging.getLogger(__name__)

path_specs = paths.read_path_spec()
bt_backup_p = paths.get_bt_backup_path()

fastresumes = fastresume.parse_all_fastresumes(bt_backup_p)

qbt_client = helpers.connect_client()

remote_hashes = helpers.get_remote_hashes(qbt_client)

ssh_details = helpers.get_ssh_creds()
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())



counts = {
    'finished': 0,
    'progressing': 0,
    'fastresume_problem': 0,
    'total_tried': 0,
    'missing_local_torrent': 0
    }


for fr in fastresumes:
    counts['total_tried'] += 1
    if not fr:
        counts['fastresume_problem'] += 1
        continue
    if not 'torrent' in fr or not fr['torrent']:
        counts['missing_local_torrent'] += 1
        continue

    for k in ['finished', 'progressing']:
        if fr['torrent_hash'] in remote_hashes[k]: counts[k] += 1

    transfer_paths = paths.translate_paths(fr['fastresume']['save_path'], path_specs)

    if not transfer_paths: continue

    renames = itertools.repeat(None)

    if 'mapped_files' in fr['fastresume']:
        renames = fr['fastresume']['mapped_files']

    for torrent_file, rename in zip(fr['torrent'].files, renames):

        file_path_rel = pathlib.Path(torrent_file.name)

        rename_path_rel = file_path_rel
        if rename: 
            rename_path_rel = pathlib.Path(rename)

            L.info(f'Local Rename: {file_path_rel} => {rename_path_rel}')

        file_path_local = transfer_paths['local'] / rename_path_rel
        file_path_remote = transfer_paths['remote'] / file_path_rel


        if rename: L.debug(f"Sending: {file_path_local} => {file_path_remote}")


print(f"{counts}")

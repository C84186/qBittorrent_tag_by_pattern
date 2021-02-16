import helpers, defs, paths, fastresume, ssh
from defs import pathlike_hint

import qbittorrentapi, yaml, progressbar, paramiko
from functools import partial
import pathlib, logging, itertools, os

dry_run = False

L = logging.getLogger(__name__)
logging.basicConfig(filename = 'out.log')
path_specs = paths.read_path_spec()
bt_backup_p = paths.get_bt_backup_path()

def mkdir_p(sftp, remote_directory):
    """Change to this directory, recursively making new folders if needed.
    Returns True if any folders were created."""
    if remote_directory == '/':
        # absolute path so change directory to root
        sftp.chdir('/')
        return
    if remote_directory == '':
        # top-level relative directory must exist
        return
    try:
        sftp.chdir(remote_directory) # sub-directory exists
    except IOError:
        dirname, basename = os.path.split(remote_directory.rstrip('/'))
        mkdir_p(sftp, dirname) # make parent directories
        sftp.mkdir(basename) # sub-directory missing, so created it
        sftp.chdir(basename)
        return True


def transfer_fastresumes(fastresume_list, remote_hashes, qbt, sftp, path_specs = paths.read_path_spec()):
    counts = {
        'finished': 0,
        'progressing': 0,
        'fastresume_problem': 0,
        'total_tried': 0,
        'missing_local_torrent': 0,
        'n_total' : len(fastresume_list)
        }

    for fr in fastresume_list:
        counts['total_tried'] += 1
        L.info(counts)
        if not fr:
            counts['fastresume_problem'] += 1
            continue
        if not 'torrent' in fr or not fr['torrent']:
            L.warn(f"Missing corresponding torrent! {fr['torrent_hash']}")
            counts['missing_local_torrent'] += 1
            continue

        for k in ['finished', 'progressing']:
            if fr['torrent_hash'] in remote_hashes[k]: counts[k] += 1
            L.info(f"{fr['torrent_hash']} for in {k}, skipping!")
            continue

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

            if not file_path_local.exists():
                L.warn(f"File: {file_path_local} not found!")
                continue

            actual_path_size = file_path_local.stat().st_size
            expected_path_size = torrent_file.length

            if actual_path_size != expected_path_size:
                L.warn(f"File Size Mismatch: {file_path_local} actual: {actual_path_size} != expected: {expected_path_size}")
                continue
            L.info(f"for {file_path_local} sizes seem to match")

            if dry_run: continue
            
            L.info(f"Sending: {file_path_local} => {file_path_remote}")
            #  print(f"Sending: {file_path_local} => {file_path_remote}")
            

            progress_widgets = [
                progressbar.Variable('i'),
                progressbar.Variable('n'),
                progressbar.DataSize(),
                progressbar.FileTransferSpeed(),
                progressbar.Bar(),
                progressbar.Variable('local_path')]


            path_progress = helpers.format_progress_path(rename_path_rel)

            with progressbar.ProgressBar(widgets = progress_widgets , max_value = torrent_file.length, redirect_stdout = True) as progress:
                updater = partial(helpers.update_progress, progress = progress, local_path = path_progress, n = counts['n_total'], i = counts['n_tried'])

                try:

                    remote_parent = file_path_remote.parent
                    stat = sftp.lstat(str(remote_parent))
                except FileNotFoundError:
                    mkdir_p(sftp, str(remote_parent))

                sftp.put(str(file_path_local), str(file_path_remote), callback = updater, confirm = True)

        if dry_run: continue

        try:
            with open(fr['torrent_path'], "rb") as torrent_file:
                status = qbt_client.torrents_add(torrent_files = {fr['torrent'].name : torrent_file}, category = fr['fastresume']['qBt-category'])
                L.info(status)
        except qbittorrentapi.exceptions.UnsupportedMediaType415Error:
            L.error(f"{fr['torrent'].name} failed - UnsupportedMediaType, {fr['torrent'].get_magnet}")
            print(status)
    return counts



fastresumes = fastresume.parse_all_fastresumes(bt_backup_p)

qbt_client = helpers.connect_client()

remote_hashes = helpers.get_remote_hashes(qbt_client)

ssh_details = helpers.get_ssh_creds()

n_fastresumes_b4 = len(fastresumes)
fastresumes = fastresume.filter_for_complete(fastresumes)

n_fastresumes_b4_checking_remote = len(fastresumes)
fastresumes = [fr for fr in fastresumes if not fr['torrent_hash'] in remote_hashes['finished']]

fastresumes = sorted(fastresumes, key = lambda i: (i['fastresume']['total_downloaded']))

with paramiko.SSHClient() as ssh_client:
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh_client.connect(
        hostname = ssh_details['hostname'],
        port = ssh_details['port'],
        username = ssh_details['username'],
        key_filename = map(str, ssh_details['key_file_path']))

    sftp_client = ssh_client.open_sftp()

    counts = transfer_fastresumes(fastresumes, remote_hashes, qbt_client, sftp_client, path_specs = path_specs)

counts['before'] = n_fastresumes_b4
counts['before_remote'] = n_fastresumes_b4_checking_remote
print(f"{counts}")

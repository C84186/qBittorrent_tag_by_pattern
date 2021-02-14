#import helpers, defs
#import qbittorrentapi, ssh, yaml
import pathlib, logging, itertools

L = logging.getLogger(__name__)

path_specs = paths.read_path_spec()
bt_backup_p = paths.get_bt_backup_path()

fastresumes = fastresume.parse_all_fastresumes(bt_backup_p)

for fr in fastresumes:
    if not fr: continue
    if not 'torrent' in fr or not fr['torrent']: continue

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

            print('---------')
            print(f'{file_path_rel} => {rename_path_rel}')

        file_path_local = transfer_paths['local'] / rename_path_rel
        file_path_remote = transfer_paths['remote'] / file_path_rel


        if rename: print(f"{file_path_local} => {file_path_remote}")


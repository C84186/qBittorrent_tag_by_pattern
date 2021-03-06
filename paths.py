import yaml, re, logging, os
from pathlib import Path, PureWindowsPath, PurePosixPath
import defs

L = logging.getLogger(__name__)

def read_path_spec(spec_file_path = defs.credentials_path):
    
    with open(spec_file_path, "r") as f:
        cfg = yaml.load(f)

    specs = cfg['path_bindings']

    if not isinstance(specs, list): 
        L.error(f"Must supply a list for 'path_bindings: in {spec_file_path}'")
        exit(1)

    if len(specs) > 1:
        L.error(f"path_bindings lists can only have one set of remote / local bindings for now")
        exit(1)

    specs = specs[0]

    allowed_keys = {'local', 'remote'}
    if set(specs.keys()) != allowed_keys:
        L.error(f"invalid top level keys for path_bindings, {specs.keys()}, expecting {allowed_keys}")
        exit(1)

    allowed_contexts = {'transfer', 'qbittorrent'}
    for k in specs:
        # for now, demand a dictionary
        if not isinstance(specs[k], dict):
            L.error(f"expecting a dict for {k}")
            exit(1)

        if set(specs[k].keys()) != allowed_contexts:
            L.error(f"expecting {allowed_contexts} for {k}")
            exit(1)

        for context in specs[k]:

            kind = type(specs[k][context]) 
            if not kind in [str, dict]:
                specs[k][context] = PurePosixPath(specs[k][context])
                L.error(f"expecting a dict or str for {k}.{context}, got {kind}")
            
            if kind == dict:
                allowed_context_keys = {'path', 'os'}
                if set(specs[k][context].keys()) != allowed_context_keys:
                    L.error(f"path_bindings[{k}][{context}] {specs[k][context].keys()}, expected {allowed_context_keys}")
                    exit(1)

                if specs[k][context]['os'].lower().startswith("w"):
                    specs[k][context] = PureWindowsPath(specs[k][context]['path'])
                else:
                    specs[k][context] = PurePosixPath(specs[k][context])

        return specs

def translate_paths(fastresume_local_path, path_spec):
    # Return a local path & a destination path
    out = {'local': None, "remote" : None}
    
    # For now we only use entry 0
    entry = path_spec

    windows_drive_pat = r'^[a-zA-Z]:\\'

    if re.match(windows_drive_pat, fastresume_local_path):
        fastresume_local_path = PureWindowsPath(fastresume_local_path)
    else:
        fastresume_local_path = PurePosixPath(fastresume_local_path)
    


    if not fastresume_local_path.is_relative_to(entry['local']['qbittorrent']):
        L.error(f"Unable to get {fast_resume_local_path} as relative to {path_spec_entry['local']['qbittorrent']}")
        return None

    relative_path = fastresume_local_path.relative_to(entry['local']['qbittorrent'])

    transfer_local_path = Path(entry['local']['transfer']) / relative_path

    out['local'] = transfer_local_path

    transfer_remote_path = Path(entry['remote']['transfer']) / relative_path
    
    out['remote'] = transfer_remote_path

    return out

def get_bt_backup_path(spec_file_path = defs.credentials_path):
    
    with open(spec_file_path, "r") as f:
        cfg = yaml.load(f)
    
    return Path(cfg['bt_backup_path'])


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

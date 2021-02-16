import defs
import yaml, qbittorrentapi

from pathlib import Path

default_creds = defs.default_creds

def connect_client(credentials_path = defs.credentials_path):

    with open(credentials_path) as f:
        creds = yaml.load(f)

    for key, value in default_creds.items():
        if not key in creds:
            print(f"{key} not given in {credentials_path}")

            if value:
                creds[key] = value
                print(f"Using default for {key} : {value}")
            else:
                print(f"Please supply {key}")
                return None

    # instantiate a Client using the appropriate WebUI configuration
    qbt_client = qbittorrentapi.Client(host=creds['hostname'], port=creds['port'], username=creds['username'], password=creds['password'])

    # the Client will automatically acquire/maintain a logged in state in line with any request.
    # therefore, this is not necessary; however, you many want to test the provided login credentials.
    try:
        qbt_client.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        print(e)

    return qbt_client


def get_remote_hashes(qbt_client):
     all_torrents = qbt_client.torrents_info()

     out = {}
     out['finished'] = { x['hash'] for x in all_torrents if x['amount_left'] == 0}

     out['progressing'] =  { x['hash'] for x in all_torrents  if x['amount_left'] > 0 }

     return out


def get_ssh_creds(creds_path = defs.credentials_path):
    with open(creds_path, 'r') as f:
        creds = yaml.load(f)

    creds = creds['ssh']

    creds['key_file_path'] = map(lambda p : Path(p).expanduser(), creds['key_file_path'])
    return creds



def update_progress(total_transferred, total_size, progress = None, **kwargs):
    if progress: progress.update(total_transferred, **kwargs)


def truncate_middle(s: str, n: int):
    if len(s) <= n:
        # string is already short-enough
        return s
    # half of the size, minus the 3 .'s
    n_2 = int(n) / 2 - 3
    # whatever's left
    n_1 = n - n_2 - 3
    return '{0}...{1}'.format(s[:n_1], s[-n_2:])

def format_progress_path(local_path : defs.pathlike_hint, width_path : int = 30):
    local_path = Path(local_path)
    parts = local_path.parts

    if len(parts) < 2: parts = ("") + (parts)

    parts = map(lambda p : '/'+truncate_middle(p, width_path), parts)
    
    return '\n'.join(parts)


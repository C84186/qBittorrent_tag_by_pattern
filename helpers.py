import defs
import yaml, typing, qbittorrentapi

from pathlib import Path, PurePath

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

    n_1 = int(n_1)
    n_2 = int(n_2)

    return '{0}...{1}'.format(s[:n_1], s[-n_2:])

def format_progress_path(rel_path : defs.pathlike_hint, width_last : int = 40, width_first : int = 20, width_total : int = 60):
    rel_path = PurePath(rel_path)

    if len(str(rel_path)) <= width_total: return str(rel_path)
    parts = rel_path.parts
    
    if len(parts) > 2:
        parts = list(parts)
        ends = [parts[0], parts[-1]]

        parts = parts[1:-1]
        parts = [ p[0] for p in parts ]

        parts = [ends[0]] + parts + [ends[-1]]

    rejoined = PurePath(*parts)

    if len(str(rejoined)) <= width_total: return str(rejoined)

    parts = rejoined.parts
    parts = list(parts)
    
    ends = [parts[0]] + [parts[-1]]
    parts = parts[1:-1]

    ends[0]  = truncate_middle(ends[0], width_first)
    ends[-1] = truncate_middle(ends[-1], width_last)

    parts = [ends[0]] + list(parts) + [ends[-1]]

    rejoined = PurePath(*parts)
    return str(rejoined)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def torrent_has_all_tags(torrent, tags : typing.Optional[list]) -> bool:
    torrent_tags = torrent.tags
    if not torrent_tags: return False
    if not tags: return True

    torrent_tags = torrent_tags.split(", ")

    all_contained = all(tag in torrent_tags for tag in tags)
    return all_contained

def torrent_lacks_any_tags(torrent, tags : typing.Optional[list]) -> bool:
    torrent_tags = torrent.tags
    if not torrent_tags: return True
    if not tags: return True

    torrent_tags = torrent_tags.split(", ")
    
    any_contained = any(tag in torrent_tags for tag in tags)
    return not any_contained

def filter_for_tags(torrent_list, has_tags : typing.Optional[list] = None, missing_tags : typing.Optional[list] = None) -> list:
    out = torrent_list
    out = [torrent for torrent in out if torrent_has_all_tags(torrent, has_tags)]

    out = [torrent for torrent in out if torrent_lacks_any_tags(torrent, missing_tags)]

    return out

import defs
import yaml, qbittorrentapi

from pathlib import PureWindowsPath, PurePosixPath

default_creds = defs.default_creds

def connect_client(credentials_path):

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

def read_path_spec(spec_file_path = defs.credentials_path):
    
    with open(spec_file_path, "r") as f:
        cfg = yaml.load(f)

    specs = cfg['path_bindings']

    if not isinstance(specs, list): 
        print(f"Must supply a list for 'path_bindings: in {spec_file_path}'")
        exit(1)

    if len(specs) > 1:
        print(f"path_bindings lists can only have one set of remote / local bindings for now")
        exit(1)

    specs = specs[0]

    allowed_keys = {'local', 'remote'}
    if set(specs.keys()) != allowed_keys:
        print("invalid top level keys for path_bindings, {specs.keys}, expecting {allowed_keys}")
        exit(1)

    allowed_contexts = {'transfer', 'qbittorrent'}
    for k in specs:
        # for now, demand a dictionary
        if not isinstance(specs[k], dict):
            print(f"expecting a dict for {k}")
            exit(1)

        if set(specs[k].keys) != allowed_contexts:
            print(f"expecting {allowed_contexts} for {k}")
            exit(1)

        for context in specs[k]:

            kind = type(specs[k][context]) 
            if not kind in [str, dict]:
                specs[k][context] = PurePosixPath(specs[k][context])
                print(f"expecting a dict or str for {k}.{context}, got {kind}")
            
            if kind == dict:
                allowed_context_keys = {'path', 'os'}
                if set(specs[k][context].keys()) != allowed_context_keys:
                    print(f"path_bindings[{k}][{context}] {specs[k][context].keys()}, expected {allowed_context_keys}")
                    exit(1)

                if specs[k][context]['os'].lower().startswith("w"):
                    specs[k][context] = PureWindowsPath(specs[k][context])
                else:
                    specs[k][context] = PurePosixPath(specs[k][context])

        return specs






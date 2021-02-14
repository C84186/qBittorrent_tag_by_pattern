import defs
import yaml, qbittorrentapi


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







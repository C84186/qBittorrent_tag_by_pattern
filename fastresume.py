import os, re, typing, click, bencodepy, json, binascii 
from pathlib import Path
from torrentool.api import Torrent

pathlike_hint = typing.Union[str, bytes, os.PathLike]

#  arr = os.listdir('.')

pattern = re.compile(r'save_path\d+:(.+).9:seed_mode')

#  for fpath in arr:
    #  if fpath.endswith(".fastresume"):
        #  with open(fpath, "rb") as f:
            #  match = re.search(pattern, f.read())
            #  if match:
                #  save_path = match.groups()[0].decode('UTF-8')
                #  torrent_hash = fpath.split(".")[0]
                #  print("-", torrent_hash+":")
                #  print("    "+save_path)


def convert(data):
    if isinstance(data, bytes):
        if data.isascii(): return data.decode('ascii')
        return binascii.hexlify(data).decode('ascii')

    if isinstance(data, dict):   return dict(map(convert, data.items()))
    if isinstance(data, tuple):  return map(convert, data)
    if isinstance(data, list):   return list(map(convert, data))
    
    return data

def parse_fastresume(fastresume_path: pathlike_hint) -> typing.Optional[dict]:
    fastresume_path = Path(fastresume_path)


    out = {}
    
    out['torrent_hash'] = fastresume_path.stem 

    #  print(json.dumps(out, sort_keys = True, indent = 4))
    if fastresume_path.suffix != ".fastresume": return None

    try:
        with open(fastresume_path, "rb") as f:
            fastresume = bencodepy.bread(f)
    except bencodepy.exceptions.BencodeDecodeError:
        print(f"{out['torrent_hash']} failed to decode!")
        return None

    fastresume = convert(fastresume)
    
    #  print(json.dumps(fastresume, sort_keys = True, indent = 4))

    out['fastresume'] = fastresume

    out['torrent'] = None
    torrent_path = fastresume_path.with_suffix('.torrent')

    try:
        torrent = Torrent.from_file(torrent_path) 
        out['torrent'] = torrent
    except FileNotFoundError:
        print(f"For {out['torrent_hash']}, no corresponding .torrent!")


    #  output_path = Path(fastresume['save_path']) / torrent['info']
    return out

def parse_all_fastresumes(bt_backup_path):
    bt_backup_path = Path(bt_backup_path)

    out = [parse_fastresume(p) for p in bt_backup_path.iterdir() if parse_fastresume(p)]
    return out

@click.command()
@click.option('--command', default = 'parse_fastresume', help = "what to do")
@click.option('--path', default = '.fastresume', help = "path of fastresume")
def cli(command: str, path: pathlike_hint):
    if command == "parse_fastresume": parse_fastresume(path)


if __name__ == "__main__":
    cli()

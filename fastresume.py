import os, re, typing, click, bencodepy, json, binascii
from pathlib import Path


keywords = {
    "qBt=category"
        }

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

def parse_fastresume(path: pathlike_hint) -> typing.Optional[dict]:
    path = Path(path)

    out = {}
    if path.suffix != ".fastresume": return None

    out['torrent_hash'] = path.name

    with open(path, "rb") as f:
        content = bencodepy.bread(f)


    content = convert(content)

    print(json.dumps(content, sort_keys=True, indent=4))
    return None

@click.command()
@click.option('--command', default = 'parse_fastresume', help = "what to do")
@click.option('--path', default = '.fastresume', help = "path of fastresume")
def cli(command: str, path: pathlike_hint):
    if command == "parse_fastresume": parse_fastresume(path)



if __name__ == "__main__":
    cli()

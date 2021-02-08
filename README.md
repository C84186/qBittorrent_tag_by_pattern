# qBittorrent_tag_by_pattern
A few python scripts for helping organize (or reorganize) qBittorrent

## Aim

Applies regex rules based on torrent name, and extension matching on files to tag torrents, so it's easier to categorize them.

## Usage

Make a file, `tags.yml` based off the provided `tags.sample.yml`
Make a file `.user_credentials.yml` containing an entry for `username` and `password` - These are your qBittorrent login details

```yaml
# .user_credentials.yml
username: admin
password: adminadmin
```

Install the requirements with `pip3 install -r requirements.txt`

Run the script: `python3 getting_started.py`

There are no CLI args, it gets all its config from the values in `tags.yml`, and in `.user_credentials.yml`

It's a fairly messy script for now, if I ever need to add to it, I'll probably refactor it.

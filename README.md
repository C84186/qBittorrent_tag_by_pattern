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
hostname: localhost
port: 8080
```

Optionally, to map between different filesystem contexts, you may add the following `path_bindings:` key.

The purpose of this is to help manage when the system that runs SFTP/rsync (the host) has a different filesystem than
the system that runs qBittorrent.

Examples of this include: 

- When qBittorrent runs in docker (A fairly wise choice)
  - In this instance, `remote:` bindings will be useful.
- If you are migrating from qBittorrent for windows to another machine, but you run this program via WSL
  - In this instance, `local` bindings will be useful.
  - If a path is a windows path, you have to define this with more complexity - 
    - Instead of 
      ```yaml
      context: 'C:\\path\to\asset'
      ```
    - Use:
      ```yaml
      context:
        os: windows
        path: 'C:\\path\to\asset'
      ```

- `local:` refers to the current system/the source paths.
- `remote:` refers to the destination system/ destination paths.
- `qBittorrent:` refers to the filesystem seen by qBittorrent.
- `transfer:` refers to the filesystem seen by sftp, or perhaps rsync

Use absolute paths

```yaml
# .user_credentials.yml

path_bindings:
  - local:
      qbittorrent: 'D:\\Downloads\qBittorrent\'
      transfer:    '/mnt/d/Downloads/'
    remote:
      qbittorrent: '/data/cool_storage/qBittorrent'
      transfer:    '/media/data/docker_media/cool_storage/qBittorrent'
  # An example where the local filesystems match
  - local: 
      qbittorrent: '/mnt/d/Downloads/'
      transfer: '/mnt/d/Downloads/'
    remote:
      qbittorrent: '/media/data/Downloads'
      transfer:    '/media/data/Downloads'

```

Install the requirements with `pip3 install -r requirements.txt`

Run the script: `python3 getting_started.py`

There are no CLI args, it gets all its config from the values in `tags.yml`, and in `.user_credentials.yml`

It's a fairly messy script for now, if I ever need to add to it, I'll probably refactor it.

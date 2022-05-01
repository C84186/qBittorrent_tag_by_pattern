import typing, os

credentials_path = '.user_credentials.yml'
tag_for_invalid_overlap = "INVALID_OVERLAP_OF_TAGS"

uncategorized_kw = '_uncategorized_only'

default_creds = {'username' : None, 'password' : None, 'hostname': 'localhost', 'port' : 8080}

pathlike_hint = typing.Union[str, bytes, os.PathLike]


placeholder_tracker = "http://localhost:80/placeholder_tracker/"

builtin_trackers = [
    "** [DHT] **",
    "** [PeX] **",
    "** [LSD] **",
    placeholder_tracker
]

tag_category = {
    "get_prefix" : "_CAT_",
    "set_prefix"  : "_SET_",
    "uncat" : ""
}

tag_tracker_managed = '_TRACKERLIST_MANAGED'
tag_tracker_was_managed = '_TRACKERLIST_WAS_MANAGED'

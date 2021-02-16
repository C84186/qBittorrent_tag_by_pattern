import typing, os

credentials_path = '.user_credentials.yml'
tag_for_invalid_overlap = "INVALID_OVERLAP_OF_TAGS"

uncategorized_kw = '_uncategorized_only'

default_creds = {'username' : None, 'password' : None, 'hostname': 'localhost', 'port' : 8080}

pathlike_hint = typing.Union[str, bytes, os.PathLike]

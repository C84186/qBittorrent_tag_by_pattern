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

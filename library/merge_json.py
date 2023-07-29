#!/usr/bin/env python
# Copyright (c) Keith Gaughan, 2007.

ANSIBLE_METADATA = {
    "metadata_version": "1.0",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: merge_json
short_description: Updates a JSON file with values
description:
  - Recursively merges a JSON/YAML datastructure into a remote JSON file.
author: "Keith Gaughan (@kgaughan)"
options:
  path:
    description:
      - Path of remote JSON file.
    required: true
  data:
    description:
      - JSON/YAML data to merge into the remote file.
      - Note that any values listed in this datastructure take precedence over
        the remote data.
    required: true
  create:
    description:
      - Create the file if it doesn't already exist
    type: bool
    default: false
  indent:
    description:
      - Amount to indent by.
    default: 2
"""

RETURN = ""

EXAMPLES = """
- name: merge some values into a file
  merge_json:
    path: /path/to/my/remote/file.json
    data:
      Show: The Flintstones
      Families:
        Flintstone:
          - Fred
          - Wilma
          - Pebbles
          - Dino
        Rubble:
          - Barney
          - Betty
          - Bamm-Bamm
"""

import json
import os

from ansible.module_utils.basic import AnsibleModule


def _merge_dicts(d1: dict, d2: dict) -> bool:
    """
    Recursively merge `d2` into `d1`, and any nested dicts therein.

    Returns `True` if something was merged.

    .. note:
        Lists are treated as values. Values merged in trump those already
        there.

        The method here is sloppy as it mutates `d1`, but for our purposes
        that doesn't matter.
    """
    changed = False
    for key in d2:
        if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
            changed = _merge_dicts(d1[key], d2[key])
        elif key not in d1 or d1[key] != d2[key]:
            d1[key] = d2[key]
            changed = True
    return changed


def main():
    module = AnsibleModule(
        argument_spec={
            "path": {"type": "path", "required": True},
            "data": {"type": "dict", "required": True},
            "create": {"type": "bool", "default": False},
            "indent": {"type": "int", "default": 2},
        },
        supports_check_mode=True,
    )

    path = module.params["path"]
    data = module.params["data"]
    create = module.params["create"]
    indent = module.params["indent"]

    exists = False
    if os.path.isfile(path):
        if not os.access(path, os.R_OK | os.W_OK):
            module.fail_json(msg=f"'{path}' not readable and writable")
        exists = True
    elif not create:
        module.fail_json(msg=f"'{path}' not found")

    if exists and os.path.getsize(path) > 0:
        try:
            with open(path, "r") as fp:
                contents = json.load(fp)
        except ValueError as exc:
            module.fail_json(msg=f"Could not load '{path}': {exc}")
        merged = _merge_dicts(contents, data)
    else:
        contents = data
        merged = True

    if merged and not module.check_mode:
        with open(path, "w") as fp:
            json.dump(
                contents,
                fp,
                indent=indent,
                separators=(",", ": "),
                sort_keys=True,
            )
    module.exit_json(changed=merged)


if __name__ == "__main__":
    main()

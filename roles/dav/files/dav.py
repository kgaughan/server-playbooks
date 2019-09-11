#!/usr/bin/env python3
#
# server.py
#

import argparse
import os

import bjoern
from wsgidav.fs_dav_provider import FilesystemProvider
from wsgidav.wsgidav_app import DEFAULT_CONFIG, WsgiDAVApp


def main():
    parser = argparse.ArgumentParser(description="Runs WsgiDAV with bjoern")
    parser.add_argument("--unix", help="Unix socket path", required=True)
    parser.add_argument("--root", help="Root directory", required=True)
    args = parser.parse_args()

    config = DEFAULT_CONFIG.copy()
    config.update(
        provider_mapping={"/": FilesystemProvider(args.root)},
        verbose=4,
        property_manager=True,
    )

    try:
        bjoern.run(WsgiDAVApp(config), "unix:" + args.unix)
    except KeyboardInterrupt:
        print("Caught Ctrl-C, shutting down...")
    finally:
        os.unlink(args.unix)


if __name__ == "__main__":
    main()

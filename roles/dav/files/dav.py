#!/usr/bin/env python3
#
# server.py
#

import argparse
import logging
import os
import sys

import bjoern
from wsgidav.fs_dav_provider import FilesystemProvider
from wsgidav.wsgidav_app import DEFAULT_CONFIG, WsgiDAVApp


def main():
    parser = argparse.ArgumentParser(description="Runs WsgiDAV with bjoern")
    parser.add_argument("--unix", help="Unix socket path", required=True)
    parser.add_argument("--root", help="Root directory", required=True)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format="%(asctime)-15s %(levelname)s %(message)s",
    )

    config = DEFAULT_CONFIG.copy()
    config.update(
        provider_mapping={"/": FilesystemProvider(args.root)},
        verbose=4,
        property_manager=True,
        http_authenticator={"trusted_auth_header": "X-Forwarded-User"},
        simple_dc={"user_mapping": {"*": True}},
    )

    if os.path.exists(args.unix):
        logging.info("Removing existing socket at %s", args.unix)
        os.unlink(args.unix)

    try:
        bjoern.run(WsgiDAVApp(config), "unix:" + args.unix)
    except KeyboardInterrupt:
        print("Caught Ctrl-C, shutting down...")


if __name__ == "__main__":
    main()

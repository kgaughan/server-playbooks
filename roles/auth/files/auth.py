#!/usr/bin/env python3
#
# auth.py: A barebones WSGI auth app for use with ngx_http_auth_request_module.
#
# The protocol is simple enough. We just need to expose an endpoint that can
# respond to a HTTP POST request, responding with 200 if the request was
# allowed, and 401 (Unauthorized) or 403 (Forbidden) if it was not, and the
# user must authenticate. In the case of the former 4xx code, the user receives
# a "WWW-Authenticate" header.
#

import argparse
from base64 import b64decode
from http import client
import logging
import os
import sys
from typing import Dict, List, Optional, Tuple
from wsgiref import simple_server

import pam

Headers = List[Tuple[str, str]]


class HTTPError(Exception):
    """
    Application wants to respond with the given HTTP status code.
    """

    def __init__(self, code: int, message: Optional[str] = None):
        if message is None:
            message = client.responses[code]
        super().__init__(message)
        self.code = code

    # pylint: disable-msg=R0201
    def headers(self) -> Headers:  # pragma: no cover
        """
        Additional headers to be sent.
        """
        return []


class NotFound(HTTPError):
    """
    Resource not found.
    """

    def __init__(self, message: Optional[str] = None):
        super().__init__(client.NOT_FOUND, message)


class BadRequest(HTTPError):
    """
    Bad request.
    """

    def __init__(self, message: Optional[str] = None):
        super().__init__(client.BAD_REQUEST, message)


class Unauthorized(HTTPError):
    """
    Unauthorized; request a HTTP Basic auth response.
    """

    def __init__(self, realm: str):
        super().__init__(client.UNAUTHORIZED)
        self.realm = realm

    def headers(self) -> Headers:
        return [("WWW-Authenticate", f'Basic realm="{self.realm}"')]


def make_status_line(code: int) -> str:
    """
    Create a HTTP status line.
    """
    return f"{code} {client.responses[code]}"


class AuthServer:
    """
    The WSGI app itself.
    """

    def __init__(self, service: str, realm: str):
        super().__init__()
        self.service = service
        self.realm = realm
        self.pam = pam.pam()

    def run(self, environ: Dict[str, str]) -> Tuple[int, Headers, List[bytes]]:
        """
        Dispatch request.
        """
        auth = environ.get("HTTP_AUTHORIZATION")
        if auth is None:
            raise Unauthorized(self.realm)
        parts = auth.split(" ", 1)
        if len(parts) == 2 and parts[0].lower() == "basic":
            creds = b64decode(parts[1]).split(b":", 1)
            if len(creds) == 2:
                if self.check(creds[0].decode(), creds[1].decode()):
                    return (client.OK, [], [])
                raise Unauthorized(self.realm)
        raise BadRequest("Bad Authorization header")

    def check(self, username: str, password: str) -> bool:
        success = self.pam.authenticate(username, password, self.service)
        logging.info("Result checking %s: %s", username, success)
        return success

    def __call__(self, environ: Dict[str, str], start_response) -> List[bytes]:
        """
        Request convert the WSGI request to a more convenient format.
        """
        try:
            code, headers, content = self.run(environ)
            start_response(make_status_line(code), headers)
        except HTTPError as exc:
            headers = exc.headers()
            if exc.code in (100, 101, 204, 304):
                # These must not send message bodies.
                content = []
            else:
                headers.append(("Content-Type", "text/plain"))
                content = [str(exc).encode()]
            start_response(make_status_line(exc.code), headers)
        return content


def main():
    parser = argparse.ArgumentParser(description="Simple WSGI auth server.")
    parser.add_argument(
        "--port",
        help="Port to bind to on localhost",
        type=int,
        default=5067,
    )
    parser.add_argument("--service", help="Service name", default="http")
    parser.add_argument("--realm", help="HTTP Realm", default="auth")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format="%(asctime)-15s %(levelname)s %(message)s",
    )

    app = AuthServer(args.service, args.realm)
    with simple_server.make_server("127.0.0.1", args.port, app) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()

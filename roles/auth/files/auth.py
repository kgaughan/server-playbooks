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
import logging
from http import client
import os
import socket
import sys
from wsgiref import simple_server

import dovecotauth


class HTTPError(Exception):
    """
    Application wants to respond with the given HTTP status code.
    """

    def __init__(self, code, message=None):
        if message is None:
            message = client.responses[code]
        super().__init__(message)
        self.code = code

    # pylint: disable-msg=R0201
    def headers(self):  # pragma: no cover
        """
        Additional headers to be sent.
        """
        return []


class NotFound(HTTPError):
    """
    Resource not found.
    """

    def __init__(self, message=None):
        super().__init__(client.NOT_FOUND, message)


class BadRequest(HTTPError):
    """
    Bad request.
    """

    def __init__(self, message=None):
        super().__init__(client.BAD_REQUEST, message)


class Unauthorized(HTTPError):
    """
    Unauthorized; request a HTTP Basic auth response.
    """

    def __init__(self, realm):
        super().__init__(client.UNAUTHORIZED)
        self.realm = realm

    def headers(self):
        return [("WWW-Authenticate", 'Basic realm="{}"'.format(self.realm))]


def make_status_line(code):
    """
    Create a HTTP status line.
    """
    return "{0} {1}".format(code, client.responses[code])


class AuthServer:
    """
    The WSGI app itself.
    """

    def __init__(self, service, mech, dap):
        super().__init__()
        self.service = service
        self.mech = mech
        self.dap = dap

    def run(self, environ):
        """
        Dispatch request.
        """
        if environ["PATH_INFO"] != "/auth":
            raise NotFound()
        auth = environ.get("HTTP_AUTHORIZATION")
        if auth is None:
            raise Unauthorized("talideon.com")
        parts = auth.split(" ", 1)
        if len(parts) == 2 and parts[0].lower() == "basic":
            decoded = b64decode(parts[1]).split(":", 1)
            if len(decoded) == 2 and self.check(decoded[0], decoded[1]):
                return (client.OK, [], [])
        raise BadRequest("Bad Authorization header")

    def check(self, username, password):
        with dovecotauth.connect(self.service, unix=self.dap) as proto:
            success, _ = proto.auth(self.mech, username, password)
        return success is True  # can be False or None

    def __call__(self, environ, start_response):
        """
        Request convert the WSGI request to a more convenient format.
        """
        try:
            code, headers, content = self.run(environ)
            start_response(make_status_line(code), headers)
            return content
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


class UnixWSGIServer(simple_server.WSGIServer):
    """
    Tweaked version of WSGIServer that uses Unix domain sockets.
    """

    address_family = socket.AF_UNIX


def main():
    parser = argparse.ArgumentParser(description="Simple WSGI auth server.")
    parser.add_argument("--unix", help="Unix socket path", required=True)
    parser.add_argument("--dap", help="Unix socket path (DAP)", required=True)
    parser.add_argument("--service", help="Service name", default="imap")
    parser.add_argument("--mech", help="SASL mechanism", default="PLAIN")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, stream=sys.stderr)

    if os.path.exists(os.unix):
        logging.info("Removing existing socket at %s", args.unix)
        os.unlink(os.unix)

    server = UnixWSGIServer(args.unix, simple_server.WSGIRequestHandler)
    server.set_app(AuthServer(args.service, args.mech, args.dap))
    server.serve_forever()


if __name__ == "__main__":
    main()

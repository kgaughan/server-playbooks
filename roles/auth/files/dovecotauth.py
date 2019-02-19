"""
A client library for the Dovecot Authentication Protocol v1.1
"""

import base64
import contextlib
import os
import socket


class DovecotAuthException(Exception):
    """
    Base class for exceptions in this module.
    """


class ConnectionException(DovecotAuthException):
    """
    Something went wrong when connecting to the socket.
    """


class UnsupportedVersion(DovecotAuthException):
    """
    The protocol version supported by the server is incompatible with this
    client.
    """


class NoSupportedMechanisms(DovecotAuthException):
    """
    The server supplied no mechanism supported by this library.
    """


@contextlib.contextmanager
def connect(service, unix=None, inet=None):
    """
    Connect to a dovecot auth endpoint.
    """
    if (unix and inet) or (unix is None and inet is None):
        raise ConnectionException("Pass either 'unix' or 'inet'")
    if unix:
        sock = socket.socket(socket.AF_UNIX)
        sock.connect(unix)
    if inet:
        sock = socket.create_connection(inet)
    try:
        yield Protocol(service, sock.makefile("rwb"))
    finally:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()


def _encode_plain(uname, pwd):
    """
    Encode a username/password pair with the SASL PLAIN mechanism.
    """
    # See https://tools.ietf.org/html/rfc4616
    return "\0{}\0{}".format(uname, pwd)


_SUPPORTED = {
    "PLAIN": _encode_plain,
}


def _parse_args(args):
    """
    Parse an argument list.
    """
    result = {}
    for arg in args:
        arg = arg.decode()
        if arg == "":
            continue
        if "=" in arg:
            key, value = arg.split("=", 1)
            result[key] = value
        else:
            result[arg] = True
    return result


def _read_line(fh):
    """
    Parse a protocol line.
    """
    line = fh.readline()
    if not line:
        return None
    return line.rstrip(b"\n\r").split(b"\t")


def _write_line(fh, *args):
    fh.write("\t".join(args).encode())
    fh.write(b"\n")
    fh.flush()


class Protocol(object):
    """
    Implements the actual authentication wire protocol. This doesn't depend
    on the underlying transport and takes a file object.
    """

    handshake_completed = False
    spid = None
    cuid = None
    cookie = None

    def __init__(self, service, fh):
        self.fh = fh
        self.service = service
        self.req_id = 0
        self.mechanisms = {}
        self._previous_cont = None

    def _do_handshake(self):
        """
        Perform the initial protocol handshake.
        """
        _write_line(self.fh, "VERSION", "1", "1")
        _write_line(self.fh, "CPID", str(os.getpid()))

        unsupported = []
        while True:
            args = _read_line(self.fh)
            if args is None:
                raise ConnectionException()
            if args[0] == b"DONE":
                break

            if args[0] == b"SPID":
                self.spid = args[1]
            elif args[0] == b"CUID":
                self.cuid = args[1]
            elif args[0] == b"COOKIE":
                self.cookie = args[1]
            elif args[0] == b"VERSION":
                if args[1] != b"1" and args[2] != b"1":
                    raise UnsupportedVersion(b".".join(args[1:]))
            elif args[0] == b"MECH":
                mech = args[1].decode()
                if mech in _SUPPORTED:
                    self.mechanisms[mech] = frozenset(args[2:])
                else:
                    unsupported.append(mech)

        if len(self.mechanisms) == 0:
            raise NoSupportedMechanisms(unsupported)

        self.handshake_completed = True

    def auth(
        self,
        mechanism,
        uname,
        pwd,
        secured=False,
        valid_client_cert=False,
        no_penalty=False,
        **kwargs
    ):
        """
        Send an auth request.
        """
        if not self.handshake_completed:
            self._do_handshake()

        self._previous_cont = None

        self.req_id += 1

        for prohibited in ("resp", "no-penalty", "secured", "valid-client-cert"):
            if prohibited in kwargs:
                del kwargs[prohibited]

        args = ["{}={}".format(key, value) for key, value in kwargs.items()]
        args.insert(0, "service=" + self.service)  # 'service' must be first.

        for flag, name in (
            (secured, "secured"),
            (valid_client_cert, "valid-client-cert"),
            (no_penalty, "no-penalty"),
        ):
            if flag:
                args.append(name)

        resp = _SUPPORTED[mechanism](uname, pwd)
        args.append("resp=" + base64.b64encode(resp.encode()).decode())

        _write_line(self.fh, "AUTH", str(self.req_id), mechanism, *args)

        response = _read_line(self.fh)
        if response[0] == b"OK":
            return True, _parse_args(response[2:])
        if response[0] == b"FAIL":
            return False, _parse_args(response[2:])
        # I don't know what else to do with continues...
        self._previous_cont = response[2]
        return None, self._previous_cont

    def cont(self):
        """
        Send CONT request.
        """
        if self._previous_cont is not None:
            _write_line(self.fh, "CONT", str(self.req_id), self._previous_cont)

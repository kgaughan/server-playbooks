#!/bin/sh
pkg info -e dovecot2 && service dovecot reload
pkg info -e nginx && service nginx reload
pkg info -e postfix && service postfix reload

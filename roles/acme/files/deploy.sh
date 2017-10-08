#!/bin/sh
pkg info -e dovecot && service dovecot reload
pkg info -e nginx && service nginx reload
pkg info -e postfix && service postfix reload

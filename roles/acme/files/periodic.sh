#!/bin/sh

if test -r /etc/defaults/periodic.conf; then
    . /etc/defaults/periodic.conf
    source_periodic_confs
fi

PATH=$PATH:/usr/local/bin:/usr/local/sbin
export PATH

: ${weekly_acme_tiny_deployscript:=/usr/local/etc/acme/deploy.sh}

case "$weekly_acme_tiny_enable" in
[Yy][Ee][Ss])
	echo
	echo "Checking Let's Encrypt certificate status:"
	/usr/local/etc/acme/acme-client.sh

	if test -x /usr/local/etc/acme/deploy.sh; then
		echo "Deploying Let's Encrypt certificates:"
		/usr/local/etc/acme/deploy.sh
	else
		echo "Skipped, deploy script does not exist or is not executable"
	fi
	;;
esac

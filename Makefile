HOSTS:=hosts
FLAGS:=
CMD:=ansible-playbook -i $(HOSTS) $(if $(wildcard ./vault-password),--vault-password-file=./vault-password,--ask-vault-pass) $(FLAGS)

default: all

clean:
	find . -name \*.retry -type f -delete
	find . -name \*.orig -type f -delete

bootstrap:
	ansible-playbook -i $(HOSTS) bootstrap.yml --ask-pass

bootstrap-do:
	ansible-playbook -i $(HOSTS) bootstrap-do.yml

all:
	$(CMD) site.yml

dav:
	$(CMD) site.yml --tags=dav

feedreaders:
	$(CMD) site.yml --tags=feedreader

mailservers:
	$(CMD) site.yml --tags=mailserver

nameservers:
	$(CMD) site.yml --tags=nameserver

torrent:
	$(CMD) site.yml --tags=torrent

webmail:
	$(CMD) site.yml --tags=webmail

webservers:
	$(CMD) site.yml --tags=webserver

xmpp:
	$(CMD) site.yml --tags=xmpp

repos:
	$(CMD) site.yml --tags=repo

upgrade:
	$(CMD) upgrade.yml

.PHONY: bootstrap bootstrap-do clean default
.PHONY: mailservers nameservers webservers xmpp
.PHONY: dav feedreaders webmail repos wireguard

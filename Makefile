HOSTS:=hosts

CMD:=ansible-playbook -i $(HOSTS) $(if $(wildcard ./vault-password),--vault-password-file=./vault-password,--ask-vault-pass) site.yml

default: all

clean:
	find . -name \*.retry -type f -delete
	find . -name \*.orig -type f -delete

bootstrap:
	ansible-playbook -i $(HOSTS) bootstrap.yml --ask-pass

bootstrap-do:
	ansible-playbook -i $(HOSTS) bootstrap-do.yml

# buildserver isn't included by default as I tend to use Synth more than
# Poudriere, but it's good to have documented.
all:
	$(CMD) --skip-tags=buildserver

dav:
	$(CMD) --tags=dav

feedreaders:
	$(CMD) --tags=feedreader

mailservers:
	$(CMD) --tags=mailserver

nameservers:
	$(CMD) --tags=nameserver

webmail:
	$(CMD) --tags=webmail

webservers:
	$(CMD) --tags=webserver

xmpp:
	$(CMD) --tags=xmpp

buildservers:
	$(CMD) --tags=buildserver

repos:
	$(CMD) --tags=repo

.PHONY: bootstrap clean default site
.PHONY: mailservers nameservers buildservers webservers xmpp
.PHONY: dav feedreaders webmail repos

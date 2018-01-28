HOSTS:=hosts

default: all

clean:
	find . -name \*.retry -type f -delete
	find . -name \*.orig -type f -delete

bootstrap:
	ansible-playbook -i $(HOSTS) bootstrap.yml --ask-pass

all:
	ansible-playbook -i $(HOSTS) site.yml --ask-vault-pass

acme:
	ansible-playbook -i $(HOSTS) site.yml --tags=acme --ask-vault-pass

dbservers:
	ansible-playbook -i $(HOSTS) site.yml --tags=dbserver --ask-vault-pass

mailservers:
	ansible-playbook -i $(HOSTS) site.yml --tags=mailserver --ask-vault-pass

nameservers:
	ansible-playbook -i $(HOSTS) site.yml --tags=nameserver --ask-vault-pass

webservers:
	ansible-playbook -i $(HOSTS) site.yml --tags=webserver --ask-vault-pass

xmpp:
	ansible-playbook -i $(HOSTS) site.yml --tags=xmpp --ask-vault-pass

buildservers:
	ansible-playbook -i $(HOSTS) site.yml --tags=buildserver --ask-vault-pass

.PHONY: bootstrap clean default site
.PHONY: mailservers nameservers buildservers dbservers webservers acme xmpp

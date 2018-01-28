HOSTS:=hosts

default: site

clean:
	find . -name \*.retry -type f -delete
	find . -name \*.orig -type f -delete

bootstrap:
	ansible-playbook -i $(HOSTS) bootstrap.yml --ask-pass

site:
	ansible-playbook -i $(HOSTS) site.yml --ask-vault-pass

acme:
	ansible-playbook -i $(HOSTS) acme.yml

dbservers:
	ansible-playbook -i $(HOSTS) dbservers.yml

mailservers:
	ansible-playbook -i $(HOSTS) mailservers.yml

nameservers:
	ansible-playbook -i $(HOSTS) nameservers.yml

webservers:
	ansible-playbook -i $(HOSTS) webservers.yml

xmpp:
	ansible-playbook -i $(HOSTS) xmpp.yml

buildservers:
	ansible-playbook -i $(HOSTS) buildservers.yml

.PHONY: bootstrap clean default site
.PHONY: mailservers nameservers buildservers dbservers webservers acme xmpp

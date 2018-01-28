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
	ansible-playbook -i $(HOSTS) acme.yml --ask-vault-pass

dbservers:
	ansible-playbook -i $(HOSTS) dbservers.yml --ask-vault-pass

mailservers:
	ansible-playbook -i $(HOSTS) mailservers.yml --ask-vault-pass

nameservers:
	ansible-playbook -i $(HOSTS) nameservers.yml --ask-vault-pass

webservers:
	ansible-playbook -i $(HOSTS) webservers.yml --ask-vault-pass

xmpp:
	ansible-playbook -i $(HOSTS) xmpp.yml --ask-vault-pass

buildservers:
	ansible-playbook -i $(HOSTS) buildservers.yml --ask-vault-pass

.PHONY: bootstrap clean default site
.PHONY: mailservers nameservers buildservers dbservers webservers acme xmpp

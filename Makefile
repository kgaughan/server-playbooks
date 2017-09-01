HOSTS:=hosts

default: site

clean:
	find . -name \*.retry -type f -delete

bootstrap:
	ansible-playbook -i $(HOSTS) bootstrap.yml --ask-pass

site:
	ansible-playbook -i $(HOSTS) site.yml

mailservers:
	ansible-playbook -i $(HOSTS) mailservers.yml

nameservers:
	ansible-playbook -i $(HOSTS) nameservers.yml

.PHONY: bootstrap clean default site
.PHONY: mailservers nameservers

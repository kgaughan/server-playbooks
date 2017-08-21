HOSTS:=hosts

default: site

clean:
	find . -name \*.retry -type f -delete

bootstrap:
	ansible-playbook -i $(HOSTS) bootstrap.yml

site:
	ansible-playbook -i $(HOSTS) site.yml

mailservers:
	ansible-playbook -i $(HOSTS) mailservers.yml

.PHONY: bootstrap clean default site
.PHONY: mailservers

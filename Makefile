HOSTS:=hosts

default: site

clean:
	find . -name \*.retry -type f -delete

bootstrap:
	ansible-playbook -i $(HOSTS) bootstrap.yml

site:
	ansible-playbook -i $(HOSTS) site.yml

.PHONY: bootstrap clean default site

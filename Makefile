default: site

clean:
	find . -name \*.retry -type f -delete

bootstrap:
	ansible-playbook -i hosts bootstrap.yml

site:
	ansible-playbook -i hosts site.yml

.PHONY: bootstrap clean default site

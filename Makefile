.PHONY: bootstrap
bootstrap:
	ansible-playbook -i hosts bootstrap.yml

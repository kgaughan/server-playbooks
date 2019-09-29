HOSTS:=hosts
FLAGS:=
CMD:=ansible-playbook -i $(HOSTS) $(if $(wildcard ./vault-password),--vault-password-file=./vault-password,--ask-vault-pass) $(FLAGS)

deploy:
	$(CMD) user.yml

.PHONY: deploy

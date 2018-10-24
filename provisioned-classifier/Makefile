.PHONY: ami run-new run-old setup up down run-cluster stack
STACK_NAME := classifier-demo2
AWS_REGION := us-west-2
PULUMI_ARGS := --skip-preview --parallel 100 --yes --non-interactive --color never
CLUSTER_SIZE ?= $(shell cat pulumi/cluster_size)

setup: env log output stack

stack:
	(. ./activate && \
	  cd pulumi && \
	  npm install -y &&\
	  (pulumi stack init $(STACK_NAME) || true) &&\
	  pulumi config set aws:region $(AWS_REGION))

env:
	virtualenv env
	. ./activate && pip install -r requirements.txt  &&\
	                pip install -r requirements.dev.txt


run-cluster: urls.txt
	@if [ -z "$(INPUT_LINES)" ]; then echo "INPUT_LINES not set"; exit 1; fi
	@(. ./activate && \
	  cd ansible && \
	  ansible-playbook -i ./inventory.yml --key-file ../ssh_key.pem  \
	    ./run.yml --extra-vars "input_lines=$(INPUT_LINES)" && \
	  cat ../$< && \
	  ansible-playbook -i ./inventory.yml --key-file ../ssh_key.pem  \
	    ./await_results.yml --extra-vars "input_lines=$(INPUT_LINES)" &&\
	  ansible-playbook -i ./inventory.yml --key-file ../ssh_key.pem  \
	    ./cluster_shutdown.yml )

get-results:
	C=`grep -a1 metrics_host ansible/inventory.yml | tail -n1 | awk '{print $$1}'` ; \
	scp -i ssh_key.pem ubuntu@$$C:/ramdisk/results/results.tgz output/

up: app.zip ONCALL.json
	@if [ -z "$(CLUSTER_SIZE)" ]; then echo "CLUSTER_SIZE not set"; exit 1; fi
	@echo "$(CLUSTER_SIZE)" > pulumi/cluster_size
	@rm -f pulumi/.up ansible/inventory.yml
	@$(MAKE) -s pulumi/.up ansible/inventory.yml
	@(. ./activate &&\
	  cd ansible && \
	  ansible-playbook -i ./inventory.yml --key-file ../ssh_key.pem  \
	    ./upload_app.yml)

ONCALL.json:
	@echo 'Setting up empty ONCALL.json'
	@echo 'Please add your phone number and run "make up" to receive status alerts'
	@echo  '[]' > $@

urls.txt: pulumi/.up
	. ./activate && cd pulumi && ./generate_links.sh > ../$@

pulumi/.up: ssh_pubkey_in_ec2_format.pub
	. ./activate && cd pulumi && \
	  pulumi up $(PULUMI_ARGS) &&\
	  touch .up

down:
	. ./activate && cd pulumi && \
	  pulumi destroy $(PULUMI_ARGS) &&\
	  rm -f .up urls.txt

ssh_key.pem:
	@yes | ssh-keygen -b 2048 -t rsa -f $@ -q -N ""
	@rm -f $@.pub

ssh_pubkey_in_ec2_format.pub: ssh_key.pem
	ssh-keygen -y -f $< > $@


app.zip: Makefile activate bin classifier requirements.txt
	zip -r $@ $^

ansible/inventory.yml: ansible pulumi/.up
	. ./activate && cd pulumi && \
	  ./generate_inventory.sh > ../$@


# RUNNING THE APP LOCALLY
ansible:
	mkdir -p ansible

input/%.csv: input
	. ./activate && \
	  ./bin/generate_input_data.py $(basename $(notdir $@)) > $@

input:
	mkdir -p input

log:
	mkdir -p log

output:
	mkdir -p output


run-locally: input log output
	@-killall -9 machida 2>/dev/null
	. ./activate && \
	INPUT_LINES=$(INPUT_LINES) OUTPUT="output/local_run" \
	  N_WORKERS=$(N_WORKERS) ./bin/run_locally.sh

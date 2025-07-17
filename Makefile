PARAM_FILE=parameters_template.json
ENV_FILE=.env
UPDATED_FILE=updated-parameters.json
DEPLOY_SCRIPT=deploy_script.sh


VALID_TARGETS := deploy update delete status logs outputs events
.PHONY: all $(VALID_TARGETS)

all: deploy

$(UPDATED_FILE): update_parameters.py $(PARAM_FILE) $(ENV_FILE)
	python3 update_parameters.py

# Pattern rule to handle deploy, update, delete, status, logs, and outputs
$(VALID_TARGETS): %: $(UPDATED_FILE) $(DEPLOY_SCRIPT)
			echo "Running $(DEPLOY_SCRIPT) $@"; \
			bash $(DEPLOY_SCRIPT) $@ || { echo "$@ script failed with exit code $$?" >&2; exit 1; }


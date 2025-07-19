PARAM_FILE=parameters_template.json
ENV_FILE=.env
ENV_FILE_GENERATED=.env.generated
UPDATED_FILE=updated-parameters.json
DEPLOY_SCRIPT=deploy_script.sh
EXPAND_VAR_SCRIPT=expand_env.sh

VALID_TARGETS := deploy update delete status logs outputs events
.PHONY: all $(VALID_TARGETS)

all: deploy

$(UPDATED_FILE): update_parameters.py $(PARAM_FILE) $(ENV_FILE_GENERATED)
	python3 update_parameters.py 

$(ENV_FILE_GENERATED):	$(ENV_FILE) $(EXPAND_VAR_SCRIPT)
			bash $(EXPAND_VAR_SCRIPT) 

# Pattern rule to handle deploy, update, delete, status, logs, and outputs
$(VALID_TARGETS): %: $(UPDATED_FILE) $(DEPLOY_SCRIPT)
			echo "Running $(DEPLOY_SCRIPT) $@"; \
			bash $(DEPLOY_SCRIPT) $@ || { echo "$@ script failed with exit code $$?" >&2; exit 1; }

.PHONY: generate-env

generate-env:
	./expand_env.sh

.PHONY: update-parameters

update-parameters: generate-env
	python update_parameters.py


 
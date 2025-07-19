import json
import os
import re

def kebab_to_camel(key):
    parts = key.strip().split('_')
    return ''.join(p.capitalize() for p in parts)

def load_env(env_file):
    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                camel_key = kebab_to_camel(key)
                env_vars[camel_key] = value.strip()
                print(f"Key={camel_key}, value={value.strip()}")
    return env_vars

def update_parameters(params_file, env_vars, output_file):
    with open(params_file) as f:
        params = json.load(f)

    for param in params:
        key = param.get("ParameterKey")
        if key in env_vars:
            param["ParameterValue"] = env_vars[key]

    with open(output_file, 'w') as f:
        json.dump(params, f, indent=2)

if __name__ == "__main__":
    ENV_FILE = ".env.generated"
    PARAM_FILE = "parameters_template.json"
    OUTPUT_FILE = "updated-parameters.json"

    env = load_env(ENV_FILE)
    update_parameters(PARAM_FILE, env, OUTPUT_FILE)
    print(f" {OUTPUT_FILE} written.")

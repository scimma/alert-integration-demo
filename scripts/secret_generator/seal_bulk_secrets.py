#!/usr/bin/env python

import base64
import os
import sys
from jinja2 import Template
import yaml
import subprocess


def seal_secret_file(secret_input_filepath):
    os.makedirs('sealed-secrets', exist_ok=True)
    secret_input_filedir, secret_input_filename = os.path.split(secret_input_filepath)
    sealed_secret_output_filepath = os.path.join('sealed-secrets', f'''sealed.{secret_input_filename}''')
    command = [
            '/bin/bash',
            '-c',
            f'ls -l "{secret_input_filepath}"',
        ]
    command = [
            '/bin/bash',
            '-c',
            f'''kubeseal \
                    --scope=cluster-wide \
                    --controller-name=sealed-secrets\
                    --controller-namespace=sealed-secrets \
                    --format=yaml \
                    --secret-file="{secret_input_filepath}" \
                    --sealed-secret-file="{sealed_secret_output_filepath}"
            '''
        ]
    print(command)
    seal_cmd = subprocess.Popen(command,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        shell=False,
        env=os.environ,
    )
    stdout, stderr = seal_cmd.communicate()
    return sealed_secret_output_filepath, stdout, stderr

def render_template(name, secrets):
    with open(os.path.join(os.path.dirname(__file__), "secret.tpl.yaml")) as f:
        templateText = f.read()
    template = Template(templateText)
    secret_yaml = yaml.safe_load(template.render(
        name=name,
        secrets=secrets,
    ))
    return yaml.dump(secret_yaml, indent=2)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate Sealed Secrets from a set of YAML-formatted secrets.')
    parser.add_argument('--file', required=True, type=argparse.FileType('r'), help='input YAML file containing secrets')
    args = parser.parse_args()
    
    secrets = yaml.safe_load(args.file)
    if not isinstance(secrets, dict) or 'secrets' not in secrets or not isinstance(secrets['secrets'], list):
        print('Input data structure must be a mapping with label "secrets" whose value is a list.')
        sys.exit(1)
    for secret in secrets['secrets']:
        if 'name' in secret:
            secret_data = []
            if isinstance(secret['data'], str):
                data = yaml.safe_load(secret['data'])
            elif isinstance(secret['data'], dict):
                data = secret['data']
            else:
                print(f'''Invalid secret data for "{secret['name']}"''')
                continue
            ## Extract secret key-value pairs and encode in base64
            for key, value in data.items():
                if [sec for sec in secret_data if sec['name'] == key]:
                    print(f'''Duplicate key found "{key}". Overwriting previous value.''')
                data_b64 = base64.encodebytes(bytes(value, 'utf-8')).decode('utf-8').replace('\n', '')
                secret_data.append({
                    'name': key,
                    'data': data_b64,
                })
            ## Render Secret manifest template and write to file
            secret_yaml = render_template(secret['name'], secret_data)
            print(f'{yaml.dump(secret_yaml, indent=2)}')
            os.makedirs('secrets', exist_ok=True)
            secret_filepath = os.path.join('secrets', f'''{secret['name']}.secret.yaml''')
            with open(secret_filepath, 'w') as out_file:
                out_file.write(secret_yaml)
            ## Seal the secret file and generate a sealed-secret YAML file
            sealed_secret_output_filepath, stdout, stderr = seal_secret_file(secret_filepath)
            print(f'''{sealed_secret_output_filepath}:\n{stdout}\n{stderr}\n''')

if __name__ == "__main__":
    main()

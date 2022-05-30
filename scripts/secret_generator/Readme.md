# Secret generator

Construct a YAML file of your desired Kubernetes Secret data:

```sh
$ cat secrets/secrets.yaml 

secrets:
- name: my-secret
  data:
    postgresql-password: "37dca6...69e63f7"
    postgresql-postgres-password: "037e55d...b391fc746"
```

Seal the secrets using the helper script:

```bash
python seal_bulk_secrets.py --file ./secrets/secrets.yaml
```

Copy the individual sealed secrets from the files generated in `./sealed-secrets` into your Helm chart `templates` folder.

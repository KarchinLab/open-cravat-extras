# ClinGen LDH data upload

Upload data from the OpenCRAVAT API to ClinGen LDH. This script was used to upload the initial data for the ClinGen Curated variants. 

## Input Data

The script expects an input file of line-separated ClinGen Allele Registry IDs. The default name is `clingen_curated_variants.tsv`.
Example:
```text
CA000069
CA114131
CA10584692
```

## Environment Variables

The script expects three environment variables (or a .env file) for the GenBoree account info and environment submission endpoint. See `example.env` for the specific variables.

## Command-line

```shell
usage: clingen_ldh_submit.py [-h] [-i IN_FILE] [-u USER] [-p PASSWORD] [--env_file ENV_FILE] [-v]

options:
  -h, --help            show this help message and exit
  -i IN_FILE, --in_file IN_FILE
                        Input file. Should be a line-separated list of ClinGen Allele Registry IDs.
  -u USER, --user USER  Genboree username
  -p PASSWORD, --password PASSWORD
                        Genboree password
  --env_file ENV_FILE   Environment variable file for ClinGen GenBoree credentials.
  -v, --verbose
```
import argparse
import os
import requests
import json
import sys
import time
import uuid
from datetime import datetime
from dateutil import tz
from dotenv import load_dotenv


keys_to_ignore = [
    'annotationErrors', 'originalInput', 'alternateAlleles'
]
crx_key_to_ignore = 'all_mappings'


def get_jwt(username, password):
    url = f'https://genboree.org/auth/usr/gb:{username}/auth'
    data = {
        "type": "plain",
        "val": password
    }
    headers = {}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    j = response.json()
    if "data" in j and "jwt" in j["data"]:
        return j["data"]["jwt"]
    else:
        raise Exception('Could not acquire jwt')


def post_to_ldh(jwt, ldh_url, ca_id, data):
    # e.g.
    # url = 'https://ldh.test.genome.network/ldh/srvc/submissions/openCRAVAT'
    url = ldh_url
    iri = f"https://run.opencravat.org/webapps/variantreport/index.html?clingen={ca_id.strip()}".strip()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {jwt}'
    }
    payload = {
        "event": {
            "type": "cg-ldh-ld-submission",
            "name": "OpenCRAVAT",
            "uuid": str(uuid.uuid4()),
            "sbj": {
                "id": ca_id,
                "iri": iri,
                "format": "alleleRegistryID",
                "type": "Variant"
            },
            "triggered": {
                "by": {
                    "host": "https://www.opencravat.org/",
                    "id": "oc_submission",
                    "iri": iri
                },
                "at": datetime.now(tz=tz.UTC).isoformat()
            }
        },
        "content": {
            "sbj": {
                "Variant": {
                    "id": ca_id
                }
            },
            "ld": {
                "OpenCRAVAT": [
                    {
                        "entId": ca_id,
                        "entIri": iri.strip(),
                        "entContent": data
                    }
                ]
            }
        }
    }
    response = requests.put(url, headers=headers, json=payload)
    response.raise_for_status()


def annotate_list(caids, assembly, jwt, ldh_url, verbose=False):
    start = time.time()
    print(f'Annotating {len(caids)} variants.')
    annotated_list = []
    error_list = []
    for i, caid in enumerate(caids):
        if i > 0 and i % 1000 == 0:
            snap = time.time()
            print(f'[{snap - start}s] {i} variants complete.')
        data = {
            'assembly': assembly,
            'clingen': caid
        }
        r = requests.post('https://run.opencravat.org/webapps/variantreport/annotate', data=data)
        j = r.json()
        for key in keys_to_ignore:
            j.pop(key, None)
        if 'crx' in j and crx_key_to_ignore in j.get('crx'):
            j.get('crx').pop(crx_key_to_ignore)
        try:
            post_to_ldh(jwt, ldh_url, caid.strip(), j)
        except Exception as e:
            error_list.append(caid)

        annotated_list.append(j)
    end = time.time()
    print(f'[{end - start}s] {len(annotated_list)} variants complete.')
    if verbose:
        print(json.dumps(annotated_list))
    if error_list:
        print("Errors:", file=sys.stderr)
        print(json.dumps(error_list, indent=2), file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in_file", help="Input file. Should be a line-separated list of ClinGen Allele Registry IDs.")
    parser.add_argument("-u", "--user", help="Genboree username")
    parser.add_argument("-p", "--password", help="Genboree password")
    parser.add_argument("--env_file", help="Environment variable file for ClinGen GenBoree credentials.")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    assembly = 'hg38'
    caid_list = []
    in_file_name = args.in_file if args.in_file else './clingen_curated_variants.tsv'
    with open(in_file_name) as in_file:
        caid_list = [x.strip() for x in in_file.readlines() if x.strip()]

    load_dotenv()
    env_file_errors = False
    USERNAME = args.user or os.environ.get('OC_CLINGEN_USERNAME')
    if not USERNAME:
        env_file_errors = True
        print("OC_CLINGEN_USERNAME environment variable or --user argument required.")
    PASSWORD = args.password or os.environ.get('OC_CLINGEN_PASSWORD')
    if not PASSWORD:
        env_file_errors = True
        print("OC_CLINGEN_PASSWORD environment variable or --password argument required.")
    LDH_URL = os.environ.get('OC_CLINGEN_LDH_URL')
    if not LDH_URL:
        env_file_errors = True
        print("OC_CLINGEN_LDH_URL environment variable required.")
    if env_file_errors:
        return
    jwt = get_jwt(USERNAME, PASSWORD)
    annotate_list(caid_list, assembly, jwt, LDH_URL, args.verbose)


if __name__ == "__main__":
    main()

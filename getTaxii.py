#!/usr/bin/env python3
import json
import uuid
import requests
from collections import OrderedDict

def fetch_all_to_one_bundle(base_url, output_file, api_token):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json"
    }

    #Get all collections
    collections_url = f"{base_url}/collections/"
    r = requests.get(collections_url, headers=headers)
    #DEBUG OPTIONS IF YA WANT EM
    #print(f"[DEBUG] GET {collections_url} -> {r.status_code}")
    #print(r.text[:200])  # Show first part of response for debugging
    r.raise_for_status()
    collections = r.json().get("collections", [])

    print(f"Found {len(collections)} collections")

    all_objects = []

    #Loop over collections
    for coll in collections:
        coll_id = coll["id"]
        print(f"\nFetching collection: {coll_id} ({coll.get('title')})")
        objects_url = f"{base_url}/collections/{coll_id}/objects/"

        more = True
        next_token = None

        while more:
            url = objects_url
            if next_token:
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}next={next_token}"

            r = requests.get(url, headers=headers)
            print(f"[DEBUG] GET {url} -> {r.status_code}")
            if r.status_code != 200:
                print(r.text)
                r.raise_for_status()

            data = r.json()

            all_objects.extend(data.get("objects", []))
            print(f"  Retrieved {len(data.get('objects', []))} objects (total so far: {len(all_objects)})")

            more = data.get("more", False)
            next_token = data.get("next")

    #Create single big bundle
    bundle_data = OrderedDict()
    bundle_data["type"] = "bundle"
    bundle_data["id"] = f"bundle--{uuid.uuid4()}"
    bundle_data["spec_version"] = "2.1"
    bundle_data["objects"] = all_objects

    #Save to file
    with open(output_file, "w") as f:
        json.dump(bundle_data, f, indent=2)

    print(f"Saved {len(all_objects)} STIX objects from {len(collections)} collections to {output_file}")


fetch_all_to_one_bundle(
    #Replace with your own url
    base_url="http://opencti:8080/taxii2/root",
    output_file="/home/<user>/Malcolm/zeek/intel/STIX/opencti_collection_bundle.json",
    api_token="<opencti API token>"
)


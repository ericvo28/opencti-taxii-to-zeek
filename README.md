# OpenCTI TAXII2 Bundle Fetcher

A Python script that pulls all STIX 2.1 objects from every collection in an OpenCTI TAXII2 server and consolidates them into a single STIX bundle JSON file — useful for bulk-importing threat intelligence into tools like Malcolm/Zeek.

---

## ⚠️ Security Warnings

> **API Token Exposure — Read Before Running**

### Hardcoded Credentials
The script contains a plaintext API token directly in the source code. **Do not commit this file to any version control system (e.g., Git) with a real token present.** Anyone with access to the file or repository history will have full access to your OpenCTI instance.

**Recommended mitigations:**
- Store the token in an environment variable and read it with `os.environ.get("OPENCTI_API_TOKEN")`
- Use a secrets manager or `.env` file (excluded via `.gitignore`)
- Rotate the token immediately if it has been exposed

### Unencrypted Traffic on Port 8080
The base URL uses `http://` (not `https://`) on port **8080**. This means:
- The API token is transmitted **in plaintext** in the `Authorization` header on every request
- Any system on the same network path can intercept the token and impersonate your client

**This script should only be run:**
- On a **fully isolated, trusted internal network** (e.g., an air-gapped lab or private VLAN)
- Over a **VPN or SSH tunnel** if the OpenCTI instance is remote
- After switching to HTTPS if the environment permits it

---

## Requirements

- Python 3.x
- [`requests`](https://pypi.org/project/requests/) library

```bash
pip install requests
```

---

## Configuration

Edit the values at the bottom of the script before running:

| Parameter | Description |
|---|---|
| `base_url` | Base URL of your OpenCTI TAXII2 root endpoint |
| `output_file` | Absolute path where the output bundle JSON will be saved |
| `api_token` | Your OpenCTI API token (see security warnings above) |

```python
fetch_all_to_one_bundle(
    base_url="http://opencti:8080/taxii2/root",
    output_file="/home/<user>/Malcolm/zeek/intel/STIX/opencti_collection_bundle.json",
    api_token="<opencti API token>"
)
```

---

## Usage

```bash
python3 fetch_opencti_bundle.py
```

The script will:
1. Query all available TAXII2 collections from the server
2. Paginate through each collection to retrieve all STIX objects
3. Combine everything into a single `bundle--<uuid>` STIX 2.1 bundle
4. Write the result to the configured output file

### Example Output

```
Found 3 collections

Fetching collection: abc123 (Malware)
[DEBUG] GET http://opencti:8080/taxii2/root/collections/abc123/objects/ -> 200
  Retrieved 142 objects (total so far: 142)
...
Saved 891 STIX objects from 3 collections to /home/user/Malcolm/zeek/intel/STIX/opencti_collection_bundle.json
```

---

## Output Format

The output is a valid **STIX 2.1 bundle**:

```json
{
  "type": "bundle",
  "id": "bundle--<uuid>",
  "spec_version": "2.1",
  "objects": [ ... ]
}
```

---

## Notes

- Pagination is handled automatically via the `more` and `next` fields in TAXII2 responses
- Duplicate objects across collections are **not** deduplicated — all objects are included as-is
- Debug logging for HTTP requests is enabled by default; comment out the `[DEBUG]` print lines to suppress it

import json
import os
import sys
from pathlib import Path

# Simple .env loader
env_path = Path(__file__).resolve().parents[1] / '.env'
if not env_path.exists():
    print('MISSING_ENV_FILE')
    sys.exit(2)

vars = {}
for line in env_path.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    if '=' in line:
        k, v = line.split('=', 1)
        vars[k.strip()] = v.strip()

endpoint = vars.get('AZURE_OPENAI_ENDPOINT')
deployment = vars.get('AZURE_OPENAI_DEPLOYMENT_NAME')
apikey = vars.get('AZURE_OPENAI_API_KEY')
apiver = vars.get('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')

if not endpoint or not deployment or not apikey:
    print('MISSING_REQUIRED_VARS')
    print('endpoint=', bool(endpoint), 'deployment=', bool(deployment), 'apikey=', bool(apikey))
    sys.exit(2)

endpoint = endpoint.rstrip('/')
uri = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={apiver}"
print('REQUEST_URI=', uri)

payload = {
    "messages": [{"role": "user", "content": "Test connection — please reply with OK."}],
    "max_tokens": 40
}

# Try requests, fallback to urllib
try:
    import requests
    r = requests.post(uri, headers={"api-key": apikey, "Content-Type": "application/json"}, json=payload, timeout=30)
    try:
        r.raise_for_status()
    except Exception:
        print('HTTP_ERROR', r.status_code)
        print(r.text)
        sys.exit(1)
    j = r.json()
    print(json.dumps(j, indent=2))
    if 'choices' in j and j['choices'] and 'message' in j['choices'][0]:
        print('\nMODEL_REPLY:\n', j['choices'][0]['message'].get('content'))
except Exception as e:
    # fallback
    import urllib.request
    req = urllib.request.Request(uri, data=json.dumps(payload).encode('utf-8'), headers={"api-key": apikey, "Content-Type": "application/json"}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode('utf-8')
            j = json.loads(data)
            print(json.dumps(j, indent=2))
            if 'choices' in j and j['choices'] and 'message' in j['choices'][0]:
                print('\nMODEL_REPLY:\n', j['choices'][0]['message'].get('content'))
    except Exception as e2:
        print('REQUEST_EXCEPTION')
        print(e)
        print(e2)
        sys.exit(1)

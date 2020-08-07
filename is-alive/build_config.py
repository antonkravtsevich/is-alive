import os
import json

data = {
    "type": os.environ.get('TYPE'),
    "project_id": os.environ.get('PROJECT_ID'),
    "private_key_id": os.environ.get('KEY_ID'),
    "private_key": os.environ.get('KEY').replace('\\n', '\n'),
    "client_email": os.environ.get('CLIENT_EMAIL'),
    "client_id": os.environ.get('CLIENT_ID'),
    "auth_uri": os.environ.get('AUTH_URI'),
    "token_uri": os.environ.get('TOKEN_URI'),
    "auth_provider_x509_cert_url": os.environ.get('PROVIDER_CERT_URL'),
    "client_x509_cert_url": os.environ.get('CLIENT_CERT_URL')
}

with open('account.json', 'w') as account_json:
    json.dump(data, account_json)
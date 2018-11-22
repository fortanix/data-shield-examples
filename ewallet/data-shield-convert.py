#!/usr/bin/python3

# To use this script, run it as:
# data-shield-convert.py <EM endpoint e.g. https://enclave-manager.domain> <registry>

import base64
import json
import ssl
import sys
import urllib.request

def json_request(path, req=None):
    url = manager_url + path

    headers = {
        "Authorization": "Basic " + token
    }

    data = None
    if req is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(req).encode('utf-8')

    request = urllib.request.Request(url, data=data, headers=headers)
    response = urllib.request.urlopen(request)

    res_body = response.read()
    return json.loads(res_body.decode("utf-8"))

if len(sys.argv) < 3:
    print("Usage: data-shield-convert.py <EM endpoint> <registry>")
    exit(1)

manager_url = sys.argv[1].rstrip('/')
dest_registry = sys.argv[2].rstrip('/')

print('Obtain your authentication token with `ibmcloud iam oauth-tokens` and enter it below.')
token = input('Token: ')

print('\nRetrieving Enclave Manager CA certificate')
zone = json_request('/api/v1/zones')
zone_ca_cert = base64.b64encode(zone['certificate'].encode('utf-8')).decode('utf-8')

#source_registry = "fortanix"
#ewallet_version = "20181205-8de6405"
source_registry = "registry.ng.bluemix.net/datashield-dev"
ewallet_version = "20181214-803cab7"

ewallet_app_params = {
    "inputImageName": source_registry + "/ewallet:" + ewallet_version,
    "outputImageName": dest_registry + "/ewallet-sgx:" + ewallet_version,
    "certificates": [
        {
            "issuer": "MANAGER_CA",
            "subject": "ewallet-app-sgx",
            "keyType": "rsa",
            "keyParam": {
                "size": 2048
            },
            "keyPath": "/etc/ewallet/key.pem",
            "certPath": "/etc/ewallet/cert.pem",
            "chainPath": "none"
        }
    ],
    "caCertificates": [
        {
            "caPath": "/etc/ssl/certs/ca-cert.pem",
            "caCert": zone_ca_cert,
        }
    ]
}

ewallet_db_params = {
    "inputImageName": source_registry + "/ewallet-db:" + ewallet_version,
    "outputImageName": dest_registry + "/ewallet-db-sgx:" + ewallet_version,
    "memSize": "2048M",
    "threads": 80,
    "certificates": [
        {
            "issuer": "MANAGER_CA",
            "subject": "ewallet-db-sgx",
            "keyType": "rsa",
            "keyParam": {
                "size": 2048
            },
            "keyPath": "/etc/mysql/server-key.pem",
            "certPath": "/etc/mysql/server-cert.pem",
            "chainPath": "none"
        }
    ],
    "caCertificates": [
        {
            "caPath": "/etc/mysql/cacert.pem",
            "caCert": zone_ca_cert,
        }
    ]
}

ewallet_nginx_params = {
    "inputImageName": source_registry + "/ewallet-nginx:" + ewallet_version,
    "outputImageName": dest_registry + "/ewallet-nginx-sgx:" + ewallet_version,
    "certificates": [
        {
            "issuer": "MANAGER_CA",
            "subject": "ewallet-nginx-sgx",
            "keyType": "rsa",
            "keyParam": {
                "size": 2048
            },
            "keyPath": "/etc/nginx/nginx-key.pem",
            "certPath": "/etc/nginx/nginx-cert.pem",
            "chainPath": "none"
        }
    ],
    "caCertificates": [
        {
            "caPath": "/etc/nginx/cacert.crt",
            "caCert": zone_ca_cert,
        }
    ]
}

def whitelist_build(conv, app_name):
    req = {}
    req['docker_image_name'] = conv['newImage'].split(':')[0]
    req['docker_version'] = conv['newImage'].split(':')[1]
    req['docker_image_sha'] = conv['imageSHA']
    req['docker_image_size'] = conv['imageSize']
    req['mrenclave'] = conv['mrenclave']
    req['mrsigner'] = conv['mrenclave'] # TODO
    req['isvprodid'] = conv['isvprodid']
    req['isvsvn'] = conv['isvsvn']
    req['app_name'] = app_name

    print(json_request('/api/v1/builds', req))

print('\nConverting ewallet-app...')
ewallet_app_response = json_request('/api/v1/tools/converter/convert-app', ewallet_app_params)
whitelist_build(ewallet_app_response, 'ewallet-app-sgx')

print(ewallet_app_response)

print('\nConverting ewallet-db...')
ewallet_db_response = json_request('/api/v1/tools/converter/convert-app', ewallet_db_params)
whitelist_build(ewallet_db_response, 'ewallet-db-sgx')

print('\nConverting ewallet-nginx...')
ewallet_nginx_response = json_request('/api/v1/tools/converter/convert-app', ewallet_nginx_params)
whitelist_build(ewallet_nginx_response, 'ewallet-nginx-sgx')

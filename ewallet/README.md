The E-Wallet sample is a simple web application demonstrating an electronic
bank account which can be funded using a credit card. The E-Wallet applications
consists of three containers, which are available on Docker Hub:

 * [The E-Wallet application](https://hub.docker.com/r/fortanix/ewallet/)
 * [MariaDB database](https://hub.docker.com/r/fortanix/ewallet-db/)
 * [NGINX frontend proxy](https://hub.docker.com/r/fortanix/ewallet-nginx/)

This example first shows how to deploy the original E-Wallet application.
It then shows how you can use IBM Cloud Data Shield to run the E-Wallet
application protected with Runtime Encryption.

To try the E-Wallet application with Data Shield, you will need to have
an IBM Kubernetes Service cluster, with Data Shield installed.

# Deploying the E-Wallet Application

To deploy the application, you must have a Kubernetes cluster and have
configured kubectl to access that cluster.

Obtain the file `ewallet.yaml` and run:

    kubectl apply -f ewallet.yaml

You can run `kubectl get svc ewallet` to see the IP where the E-Wallet service
is running. Open the web UI by entering that IP in your browser.

# Deploying the E-Wallet Application with Data Shield

To deploy the application with Data Shield, you must have an IBM Kubernetes
Service cluster with Data Shield installed, and you must have set up the
container conversion service to have access to a docker registry.

Retrieve the root certificate from your Enclave Manager installation and
base64-encode it by running:

    curl https://<enclave manager>/api/v1/zones | jq -r .certificate | base64 -w0

Follow the instructions in the Data Shield helm README to set up an environment
where you can run `curl` commands against the container converter.

Create conversion template files `ewallet.json`, `ewallet-db.json`, and
`ewallet-nginx.json` by following the samples below. Replace `<your registry>`
with a registry that your converter has push access to, and replace `<base64
encoded zone certificate>` with the zone certificate above.

Repeat the following `curl` command for each of the three E-Wallet components.
Save the output from the converter for use in build whitelisting. Note that the
conversion process can take several minutes.

    curl -H 'Content-Type: application/json' -d @ewallet-app.json https://<enclave manager>/api/v1/tools/converter/convert-app
    curl -H 'Content-Type: application/json' -d @ewallet-db.json https://<enclave manager>/api/v1/tools/converter/convert-app
    curl -H 'Content-Type: application/json' -d @ewallet-nginx.json https://<enclave manager>/api/v1/tools/converter/convert-app

Use the following curl command as a template to whitelist a build in Enclave
Manager.  Replace the `<...>` with the output from the converter. Repeat this
step for each of the E-Wallet components. The converter does not yet report
MRSIGNER values. This value is used only for tracking, so you can substitute
the same value as MRENCLAVE for now.

    curl -X POST https://<enclave manager>/api/v1/builds -d '{"docker_image_name": "ewallet-app-sgx", "docker_version": "latest", "docker_image_sha": "<...>", "docker_image_size": <...>, "mrenclave": "<...>", "mrsigner": "<same as mrenclave>", "isvprodid": 1, "isvsvn": 1, "app_name": "ewallet-app-sgx"}' -H 'Content-type: application/json'

After you have created the builds, open the Enclave Manager web interface,
navigate to the Tasks view, and approve the builds.

To run the E-Wallet sample in SGX, obtain the file `ewallet-data-shield.yaml`
and replace `<your registry>` as appropriate, then run:

    kubectl apply -f ewallet-data-shield.yaml

You can run `kubectl get svc ewallet-sgx` to see the IP where the E-Wallet
service is running.

# Conversion request templates

ewallet-app.json

    {
      "inputImageName": "fortanix/ewallet:20181205-8de6405",
      "outputImageName": "<your registry>/ewallet-sgx:20181205-8de6405",
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
          "caCert": "<base64 encoded zone certificate>"
        }
      ]
    }

ewallet-db.json

    {
      "inputImageName": "fortanix/ewallet-db:20181205-8de6405",
      "outputImageName": "<your registry>/ewallet-db-sgx:20181205-8de6405",
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
          "caCert": "<base64 encoded zone certificate>"
        }
      ]
    }

ewallet-nginx.json

    {
      "inputImageName": "fortanix/ewallet-nginx:20181205-8de6405",
      "outputImageName": "<your registry>/ewallet-nginx-sgx:20181205-8de6405",
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
          "caCert": "<base64 encoded zone certificate>"
        }
      ]
    }

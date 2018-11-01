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

Follow the instructions in the Data Shield helm README to set up an environment
where you can run `curl` commands against the container converter.

Use the following `curl` commands to convert the E-Wallet containers for Data
Shield. Replace `<your-registry>` with a registry your converter has push
access to. Note that the conversion process can take several minutes.

    curl -k -H 'Content-Type: application/json' -d '{"inputImageName": "fortanix/ewallet:20181031-4732528", "outputImageName": "<your-registry>/ewallet-sgx:20181031-4732528"}' https://datashield-enclaveos-converter.default.svc.cluster.local/v1/convert-image
    curl -k -H 'Content-Type: application/json' -d '{"inputImageName": "fortanix/ewallet-db:20181031-4732528", "outputImageName": "<your-registry>/ewallet-db-sgx:20181031-4732528"}' https://datashield-enclaveos-converter.default.svc.cluster.local/v1/convert-image
    curl -k -H 'Content-Type: application/json' -d '{"inputImageName": "fortanix/ewallet-nginx:20181031-4732528", "outputImageName": "<your-registry>/ewallet-nginx-sgx:20181031-4732528"}' https://datashield-enclaveos-converter.default.svc.cluster.local/v1/convert-image

Obtain the file `ewallet-data-shield.yaml` and replace `<your-registry>` as
appropriate, then run:

    kubectl apply -f ewallet-data-shield.yaml

You can run `kubectl get svc ewallet-sgx` to see the IP where the E-Wallet
service is running.

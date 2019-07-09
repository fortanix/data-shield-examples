The Open Liberty REST Intro demonstrates a simple Java web service using
Open Liberty. The original may be found
at https://openliberty.io/guides/rest-intro.html. The container for the sample
is available on [Docker Hub](https://hub.docker.com/r/fortanix/open-liberty-rest-intro/)

This example first shows how to deploy the original sample application.
It then shows how you can use IBM Cloud Data Shield to run the sample
application protected with Runtime Encryption.

To try the sample application with Data Shield, you will need to have
an IBM Kubernetes Service cluster, with Data Shield installed.

# Deploying the Sample Application

To deploy the application, you must have a Kubernetes cluster and have
configured kubectl to access that cluster.

Obtain the file `open-liberty-rest-intro.yaml` and run:

    kubectl apply -f open-liberty-rest-intro.yaml

You can run `kubectl get svc open-liberty-rest-intro` to see the IP where the
application is running. You can use the following curl command to interact
with the application:

    curl http://<IP>/rest-1.0-SNAPSHOT/System/properties

# Deploying the Sample Application with Data Shield

To deploy the application with Data Shield, you must have an IBM Kubernetes
Service cluster with Data Shield installed, and you must have set up the
container conversion service to have access to a docker registry.

Follow the instructions in the Data Shield helm README to set up an environment
where you can run `curl` commands against the container converter.

Use the following `curl` commands to convert the sample container for Data
Shield. Replace `<your-registry>` with a registry your converter has push
access to. Note that the conversion process can take several minutes.

    curl -H 'Content-Type: application/json' -d '{"inputImageName": "fortanix/open-liberty-rest-intro:20190703-8ef3602", "outputImageName": "<your-registry>/open-liberty-rest-intro-sgx:20190219-423b695", "threads": 128, "javaMode": "LIBERTY-JRE", "rwDirs" : ["/opt/ol/wlp/output", "/logs"] }' -H "Authorization: Basic $token"  https://enclave-manager.<ingress-domain>/api/v1/tools/converter/convert-app

Obtain the file `open-liberty-rest-intro-data-shield.yaml` and replace
`<your-registry>` as appropriate, then run:

    kubectl apply -f open-liberty-rest-intro-data-shield.yaml

You can run `kubectl get svc open-liberty-rest-intro-sgx` to see the IP where
the sample service is running. You can interact with the shielded version of
the application using the same curl command given above for the unshielded
version. You may have to wait several minutes for the shielded version of
the application to start.

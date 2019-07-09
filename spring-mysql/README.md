The Spring MySQL sample demonstrates a simple Java application written using
the Spring framework, that accesses a MySQL database. The original may be found
at https://spring.io/guides/gs/accessing-data-mysql/. The sample consists of
two containers, which are available on Docker Hub:

 * [The application](https://hub.docker.com/r/fortanix/spring-mysql-app/)
 * [The database](https://hub.docker.com/r/fortanix/spring-mysql-db/)

This example first shows how to deploy the original sample application.
It then shows how you can use IBM Cloud Data Shield to run the sample
application protected with Runtime Encryption.

To try the sample application with Data Shield, you will need to have
an IBM Kubernetes Service cluster, with Data Shield installed.

# Deploying the Sample Application

To deploy the application, you must have a Kubernetes cluster and have
configured kubectl to access that cluster.

Obtain the file `spring-mysql.yaml` and run:

    kubectl apply -f spring-mysql.yaml

You can run `kubectl get svc spring-mysql` to see the IP where the application
is running. You can use the following curl commands to interact with the
application:

    curl 'http://<IP>/demo/add?name=User&email=user@example.com'
    curl 'http://<IP>/demo/all'

# Deploying the Sample Application with Data Shield

To deploy the application with Data Shield, you must have an IBM Kubernetes
Service cluster with Data Shield installed, and you must have set up the
container conversion service to have access to a docker registry.

Follow the instructions in the Data Shield helm README to set up an environment
where you can run `curl` commands against the container converter.

Use the following `curl` commands to convert the Spring-MySQL sample containers
for Data Shield. Replace `<your-registry>` with a registry your converter has
push access to. Note that the conversion process can take several minutes.

    curl -H 'Content-Type: application/json' -d '{"inputImageName": "fortanix/spring-mysql-app:20190703-8ef3602", "outputImageName": "<your-registry>/spring-mysql-app-sgx:20190206-220832d", "threads": 128, "javaMode" : "OPENJDK", "encryptedDirs" : ["/tmp"] }' -H "Authorization: Basic $token"  https://enclave-manager.<ingress-domain>/api/v1/tools/converter/convert-app
    curl -H 'Content-Type: application/json' -d '{"inputImageName": "fortanix/spring-mysql-db:20190703-8ef3602", "outputImageName": "<your-registry>/spring-mysql-db-sgx:20190206-220832d", "threads": 80, "encryptedDirs" : ["/var/lib/_mysql", "/etc/mysql","/tmp","/run/mysqld"]}' -H "Authorization: Basic $token"  https://enclave-manager.<ingress-domain>/api/v1/tools/converter/convert-app

Obtain the file `spring-mysql-data-shield.yaml` and replace `<your-registry>` as
appropriate, then run:

    kubectl apply -f spring-mysql-data-shield.yaml

You can run `kubectl get svc spring-mysql-sgx` to see the IP where the
Spring-MySQL service is running. You can interact with the shielded version of
the application using the same curl commands given above for the unshielded
version.

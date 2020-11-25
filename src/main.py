#!/usr/bin/python3

import os
import pint
import time

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

def exec_commands(api_instance):
    name = 'calc-test'
    ns = 'calc'
    resp = None
    try:
        resp = api_instance.read_namespaced_pod(name=name,
                                                namespace=ns)
    except ApiException as e:
        if e.status != 404:
            print("Unknown error: %s" % e)
            exit(1)

    if not resp:
        print("Pod %s does not exist. Creating it..." % name)
        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": name
            },
            "spec": {
                "containers": [{
                    "name": name,
                    "image": "grzesrap/calc",
                    "env": [{
                        "name": "REDIS_HOST",
                        "value": "redis-master"
                    }],
                    "volumeMounts": [{
                        "name": "config-volume",
                        "mountPath": "/code/input"
                    }]
                }],
                "volumes": [{
                    "name": "config-volume",
                    "configMap": {
                    "name": "calc-input-config"
                    }
                }],
                "restartPolicy": "Never"
            }
        }

        resp = api_instance.create_namespaced_pod(body=pod_manifest,
                                                  namespace=ns)
        while True:
            resp = api_instance.read_namespaced_pod(name=name,
                                                    namespace=ns)
            if resp.status.phase != 'Pending':
                break
            time.sleep(1)
        print("Done.")

def main():
    config.load_kube_config()
    # config.load_incluster_config()
    v1=client.CoreV1Api()
    
    exec_commands(v1)

    # ret = v1.list_namespaced_pod(namespace=ns)
    # for i in ret.items:
    #     print("%s  %s  %s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

if __name__ == '__main__':
    main()

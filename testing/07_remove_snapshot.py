from PyXtremIO.rest_xtremio import RestFunctions
import pprint


username = "admin"
password = "Xtrem10"
hostname = "192.168.146.128"
port = "443"
xioapi_version = "v2"
cluster_name = "xbrick615"

# Information:
snapshot_set_name = "lnxprod02_dev"


#### Snapshot Management

ru = RestFunctions(username=username, password=password, server_ip=hostname, port=port, xioapi_version=xioapi_version)

msg, sts = ru.remove_snapshot_set(ss_set_name=snapshot_set_name, cluster_name=cluster_name)
if sts == 201 or sts == 200:
    print("Snapshot Deletion As Per Request!")
    pprint.pprint(msg)
else:
    print("Issue: There was an issue during creating snapshot.")
    print(msg)
from PyXtremIO.rest_xtremio import RestFunctions
import pprint


username = "admin"
password = "Xtrem10"
hostname = "192.168.146.128"
port = "443"
xioapi_version = "v2"
cluster_name = "xbrick615"

# Information:
cg_name = "cg_lnxprod02"  # consistency group name
snapshot_set_name = "lnxprod02_dev"
snap_suffix = "dev"


#### Snapshot Management

ru = RestFunctions(username=username, password=password, server_ip=hostname, port=port, xioapi_version=xioapi_version)

msg, sts = ru.create_snapshot_from_consistency_group(cg_name=cg_name, cluster_name=cluster_name,
                                                     snapshot_set_name=snapshot_set_name, snap_suffix=snap_suffix)
if sts == 201 or sts == 200:
    print("Snapshot Created As Per Request!")
    pprint.pprint(msg)
else:
    print("Issue: There was an issue during creating snapshot.")
    print(msg)
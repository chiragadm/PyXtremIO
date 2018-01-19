from PyXtremIO.rest_xtremio import RestFunctions
import pprint


username = "admin"
password = "Xtrem10"
hostname = "192.168.146.128"
port = "443"
xioapi_version = "v2"
cluster_name = "xbrick615"

# Host Information:
ig_name = "Lnxprod02"  # e.g. hostname or initiator name
vol_list = ["LnxprodVol01", "LnxprodVol02", "LnxprodVol03", "LnxprodVol04", "LnxprodVol05"]  # Volume list


#### Provisioning Storage

ru = RestFunctions(username=username, password=password, server_ip=hostname, port=port, xioapi_version=xioapi_version)

msg, sts = ru.unmap_multiple_volumes_from_ig(ig_name=ig_name, volume_list=vol_list, cluster_name=cluster_name)
if sts is True:
    print("Storage Unallocated As Per Request!")
    pprint.pprint(msg)
else:
    print("Issue: There was an issue during storage allocation.")
    print(msg)
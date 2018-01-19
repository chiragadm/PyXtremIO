from PyXtremIO.rest_xtremio import RestFunctions
import pprint


username = "admin"
password = "Xtrem10"
hostname = "192.168.86.43"
port = "443"
xioapi_version = "v2"
cluster_name = "xbrick615"

# Host Information:
ig_name = "Lnxprod01"  # e.g. hostname or initiator name
num_of_vols = 5  # total number of volumes
vol_size = "2g"  # volume size
volume_prefix_name = "LnxprodVol"  # volume name start with
volume_suffix_count = 11  # volume number starting count
cg_name = "cg_lnxprod01"  # consistency group name

#### Provisioning Storage

ru = RestFunctions(username=username, password=password, server_ip=hostname, port=port, xioapi_version=xioapi_version)

msg, sts = ru.map_new_volumes_to_existing_fc_ig(ig_name=ig_name, volume_prefix_name=volume_prefix_name,
                                                volume_suffix_count=volume_suffix_count,num_of_volumes=num_of_vols,
                                                volume_size=vol_size, cluster_name=cluster_name, cg_name=cg_name)
if sts is True:
    print("Storage Allocated As Per Request!")
    pprint.pprint(msg)
else:
    print("Issue: There was an issue during storage allocation.")
    print(msg)
from PyXtremIO.rest_xtremio import RestFunctions
import pprint


username = "admin"
password = "Xtrem10"
hostname = "192.168.86.43"
port = "443"
xioapi_version = "v2"
cluster_name = "xbrick615"

# Host Information:
ig_name = "Lnxprod02"  # e.g. hostname or initiator name
ig_os = "linux" # host operating system
wwpn_list = ["5000000000000003", "5000000000000004"]  # wwpn list
vol_list = ["LnxprodVol11", "LnxprodVol12", "LnxprodVol13", "LnxprodVol14", "LnxprodVol15"]  # Volume List
cg_name = "cg_lnxprod02"  # consistency group name

#### Provisioning Storage

ru = RestFunctions(username=username, password=password, server_ip=hostname, port=port, xioapi_version=xioapi_version)

msg, sts = ru.map_existing_volumes_to_new_fc_ig(ig_name=ig_name, ig_os=ig_os, wwpn_list=wwpn_list,
                                                volume_list=vol_list, cluster_name=cluster_name, cg_name=cg_name)
if sts is True:
    print("Storage Allocated As Per Request!")
    pprint.pprint(msg)
else:
    print("Issue: There was an issue during storage allocation.")
    print(msg)
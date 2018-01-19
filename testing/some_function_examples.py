# The MIT License (MIT)
# Copyright (c) 2016 Dell Inc. or its subsidiaries.

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
Sample Performance Script to gather an hour of data at Given a Storage group
will collect Array, Storage Group, Port Group, and Host
or Cluster level Metrics.
"""
#from PyU4V import RestFunctions

import pprint
import json
from PyXtremIO.rest_xtremio import RestFunctions
from PyXtremIO.utils import exception

ru = RestFunctions(username="admin", password="Xtrem10", server_ip="192.168.86.43",
                 port="443", xioapi_version='v2')

import time

end_date = int(round(time.time()) * 1000)
start_date = (end_date - 3600000)
sg_id = "YOURSG"
cluster_name = "xbrick615"


def get_info():
    #cls, _ = ru.get_clusters()
    #cts_grps, _ = ru.get_consistency_groups(cluster_name)
    #init_grps, _ = ru.get_initiator_groups(cluster_name)
    #volumes, _ = ru.get_volumes(cluster_name)
    #inits, _ = ru.get_initiators(cluster_name)
    #ss, _ = ru.get_snapshots(cluster_name)
    #sss, _ = ru.get_snapshot_sets(cluster_name)
    #t, _ = ru.get_tags(cluster_name)
    #lm, _ = ru.get_lun_map(cluster_name)
    #create_vol, create_vol_sts = ru.create_volume("Chirag101", "1z", cluster_name)
    #print("create_vol return msg")
    #print(create_vol)
    #print("create_vol_sts return status")
    #print(create_vol_sts)
    try:
        #create_vol, create_vol_sts = ru.create_linked_consistency_group("cg_chirag03", "cg_chirag03_link", cluster_name, repurpose_copy_flag=True, new_volume_suffix="linked")
        create_vol, create_vol_sts = ru.create_initiator_group("IG_Testing02", cluster_name)
        print("create_vol return msg")
        print(create_vol)
        print("create_vol_sts return status")
        print(create_vol_sts)
    #except exception.VolumeBackendAPIException:
    except ValueError:
        print("VolumeBackEndAPIException Occurd")
    #rename_vol, rename_sts = ru.rename_volume("ChiragPatel01", "Chirag100", cluster_name)
    #resize_vol, resize_sts = ru.increase_volume_size("Chirag100", "10g", cluster_name)
    #enable_smio_vol, enable_smio_vol_sts = ru.enable_small_io_alert_on_volume("Chirag100", cluster_name)
    #disable_smio_vol, disable_smio_vol_sts = ru.disable_small_io_alert_on_volume("Chirag100", cluster_name)
    #noaccess_vol, noaccess_vol_sts = ru.enable_noaccess_on_volume("Chirag100", cluster_name)
    #ru.enable_readaccess_on_volume("Chirag100", cluster_name)
    #ru.enable_writeaccess_on_volume("Chirag100", cluster_name)
    #ru.enable_mgmtlock_on_volume("Chirag100", cluster_name)
    #ru.disable_mgmtlock_on_volume("Chirag100", cluster_name)
    #rem_vol, rem_vol_sts = ru.remove_volume("Chirag100", cluster_name)
    #rem_vol, rem_vol_sts = ru.remove_volume("Chirag100", "abcd")
    #create_ig, create_ig_sts = ru.create_initiator_group("IG_Testing01", cluster_name)
    #init_wwn = ['20:02:61:00:00:00:00:9c']
    #init_wwn = ['lnx01-fc-1']
    #create_ig, create_ig_sts = ru.create_initiator_group("IG_Testing02", cluster_name, init_wwn)
    #create_init, create_init_sts = ru.create_initiator("Test02", '20:02:61:00:00:00:00:9b', "linux", "IG_Testing01", cluster_name)
    #create_init, create_init_sts = ru.create_initiator("lnx01-fc-4", '20:02:61:00:00:00:00:9C', "linux", "lnx01",
    #                                                   cluster_name)
    #rename_init, rename_init_sts = ru.rename_initiator("Test20", "Test02", cluster_name)
    #remove_init, remove_init_sts = ru.remove_initiator("Test04", cluster_name)
    #rename_ig, rename_ig_sts = ru.rename_initiator_group("IG_Testing01", "IG_Chirag01", cluster_name)
    #rm_ig, rm_ig_sts = ru.remove_initiator_group("IG_Chirag01", cluster_name)
    #create_cg, create_cg_sts = ru.create_consistency_group("cg_chirag10", cluster_name)
    #create_link_cg, create_link_cg_sts = ru.create_linked_consistency_group("cg_chirag03", "cg_chirag03_link", cluster_name, repurpose_copy_flag=True, new_volume_suffix="linked")
    #create_link_cg, create_link_cg_sts = ru.create_linked_consistency_group("cg_src01", "cg_src02_link", cluster_name)
    #create_link_cg, create_link_cg_sts = ru.create_linked_consistency_group("cg_chirag03_link",
    #                                                                        cluster_name)
    #create_link_cg, create_link_cg_sts = ru.create_linked_consistency_group("cg_src01", "cg_src04_dev", "ture",
    #                                                                       cluster_name, new_volume_suffix="dev")
    #refresh_link_cg_dr, refresh_link_cg_dr_sts = ru.refresh_linked_consistency_group_dryrun("cg_src01", "cg_src04_dev",
    #                                                                                        "True", "True", cluster_name)
    #refresh_link_cg, refresh_link_cg_sts = ru.refresh_linked_consistency_group("cg_src01", "cg_src04_dev", "ture",
    #                                                                                         cluster_name, "true")
    #refresh_link_cg_msv, refresh_link_cg_msv_sts = ru.refresh_linked_consistency_group_ignore_missalign_vols("cg_src01", "cg_src04_dev", "True", "true", cluster_name)
    #rename_cg, rename_cg_sts = ru.rename_consistency_group("cg_src04_link", "cg_src04_dev", cluster_name)
    #rm_cg, rm_cg_sts = ru.remove_consistency_group("cg_chirag02", cluster_name)
    #add_vol_cg, add_vol_cg_sts = ru.add_volume_to_consistency_group("cg_src01", "test01", cluster_name)
    #na_cg, na_cg_sts = ru.enable_noaccess_on_consistency_group("cg_src01", cluster_name)
    #na_cg, na_cg_sts = ru.enable_readaccess_on_consistency_group("cg_src01", cluster_name)
    #na_cg, na_cg_sts = ru.enable_writeaccess_on_consistency_group("cg_src01", cluster_name)
    #rm_vol_cg, rm_vol_sts = ru.remove_volume_from_consistency_group("cg_src01", "test01", cluster_name)
    #ss_info, ss_info_sts = ru.get_snapshot_info("SRC3.dev", cluster_name)
    #sss_info, sss_info_sts = ru.get_snapshot_set_info("SnapshotSet.1515432926964", cluster_name)
    #create_ss_cg, create_ss_cg_sts = ru.create_snapshot_from_consistency_group("cg_src01", cluster_name, snapshot_set_name="SRC01_DEV1", snap_suffix="DEV1")
    #create_ss_cg, create_ss_cg_sts = ru.create_snapshot_from_snapshot_set_name("SRC01_DEV1", cluster_name,
    #                                                                           snapshot_set_name="SRC01_DEV1_LINK",
    #                                                                           snap_suffix="DEV1_LINK")
    #vol_list = ["SRC1", "SRC2", "SRC3"]
    #create_ss_cg, create_ss_cg_sts = ru.create_snapshot_from_volumelist(vol_list, cluster_name,
    #                                                                           snapshot_set_name="PROD",
    #                                                                           snap_suffix="PROD")
    #remove_ss_cg, remove_ss_cg_sts = ru.remove_snapshot("SRC2.DEV1.DEV1_LINK", cluster_name)
    #rename_sss_cg, rename_sss_cg_sts = ru.rename_snapshot_set("SRC01_DEV1_LINK", "SRC01_Chirag", cluster_name)
    #remove_sss_cg, remove_sss_cg_sts = ru.remove_snapshot_set("SRC01_DEV1", cluster_name)
    #t_info, t_info_sts = ru.get_tag_info("/Volume/prod", cluster_name)
    #create_tag, create_tag_sts = ru.create_tag("Volume", "chirag")
    #rename_tag, rename_tag_sts = ru.rename_tag("/Volume/chirag", "patel")
    #tag_obj, tag_obj_sts = ru.tag_object("SRC1", "/Volume/patel", "Volume", cluster_name)
    #untag_obj, untag_obj_sts = ru.untag_object("SRC1", "/Volume/patel", "Volume", cluster_name)
    #rm_tag, rm_tag_sts = ru.remove_tag("/Volume/patel")
    #create_lm, create_lm_sts = ru.create_lun_map("SRC2", "lnx03", cluster_name)
    #rm_map, rm_map_sts = ru.unmap_volume_from_ig("ESXVol14_01", "esx14", cluster_name)
    #rm_map, rm_map_sts = ru.unmap_multiple_volumes_from_ig(["ESXVol14_02", "ESXVol14_03"], "esx14", cluster_name)

    #updated_volumes, _ = ru.get_volumes(cluster_name)
    #updated_ig, _ = ru.get_initiator_groups(cluster_name)
    #updated_inits, _ = ru.get_initiators(cluster_name)
    #updated_cgs, _ = ru.get_consistency_groups(cluster_name)
    #updated_ss, _ = ru.get_snapshots(cluster_name)
    #updated_sss, _ = ru.get_snapshot_sets(cluster_name)
    #updated_t, _ = ru.get_tags(cluster_name)
    #updated_lm, _ = ru.get_lun_map(cluster_name)


    #cts_grp_info, _ = ru.get_consistency_group_info("cg_lnx01", cluster_name)
    #init_grp_info, _ = ru.get_initiator_group_info("lnx01", cluster_name)
    #volume_info, _ = ru.get_volume_info("test01")
    #init_info, sts = ru.get_initiator_info("lnx01-fc-31", cluster_name)
    #print("MSG: %s | STS: %s" % (init_info, sts))
    #init_search, init_search_sts = ru.search_initiator_by_wwn("21:00:00:24:ff:5f:61:9a", cluster_name)
    #init_search, _ = ru.search_initiator_by_wwn("21:00:00:24:ff:5f:61:9a")
    #init_search, _ = ru.search_initiator_by_wwn("21:00:00:24:ff:5f:61:9b", "xbrick615")
    #lm_info, _ = ru.get_lun_map_info("1_1_1", cluster_name)

    #print(cls.get('clusters')[0].get('name'))
    #[x.get('key3') for x in dict_list[1:3]]
    #print([x.get('name') for x in cls.get('clusters')])
    #print([x.get('name') for x in cts_grps.get('consistency-groups')])
    #print([x.get('name') for x in init_grps.get('initiator-groups')])
    #print([x.get('name') for x in volumes.get('volumes')])
    #print([x.get('name') for x in inits.get('initiators')])
    #print([x.get('name') for x in ss.get('snapshots')])
    #print([x.get('name') for x in t.get('tags')])
    #print([x.get('name') for x in lm.get('lun-maps')])

    #print("cts_grp_info on cg_lnx01")
    #print(cts_grp_info)

    #print("init_grp_info on lnx01")
    #print(init_grp_info)

    #print("init_info on lnx01-fc-2")
    #print(init_info)

    #print("volume_info on test01")
    #print(volume_info)

    #print("lun map info on 2_1_1")
    #pprint.pprint(lm_info)
    #print(lm_info.get('content').get('ig-name'))

    #print("init_search on 21:00:00:24:ff:5f:61:9a")
    #pprint.pprint(init_search)
    #print("init_search_sts status code")
    #print(init_search_sts)
    #jd = json.loads(init_search)
    #pprint.pprint(init_search)

    #print("rename_vol return msg")
    #print(rename_vol)
    #print("rename_vol return status")
    #print(rename_sts)

    #print("resize_vol return msg")
    #print(resize_vol)
    #print("resize_vol return status")
    #print(resize_sts)

    #print("enable_smio_vol return msg")
    #print(enable_smio_vol)
    #print("renable_smio_vol_sts return status")
    #print(enable_smio_vol_sts)

    #print("disable_smio_vol return msg")
    #print(disable_smio_vol)
    #print("disable_smio_vol_sts return status")
    #print(disable_smio_vol_sts)

    #print("noaccess_vol return msg")
    #print(noaccess_vol)
    #print("noaccess_vol_sts return status")
    #print(noaccess_vol_sts)

    #print("rem_vol return msg")
    #print(rem_vol)
    #print("rem_vol_sts return status")
    #print(rem_vol_sts)

    #print("Updated Volume List")
    #print([x.get('name') for x in updated_volumes.get('volumes')])

    #print("create_ig return msg")
    #print(create_ig)
    #print("create_ig_sts return status")
    #print(create_ig_sts)

    #print("create_init return msg")
    #print(create_init)
    #print("create_init_sts return status")
    #print(create_init_sts)

    #print("rename_init return msg")
    #print(rename_init)
    #print("rename_init_sts return status")
    #print(rename_init_sts)

    #print("remove_init return msg")
    #print(remove_init)
    #print("remove_init_sts return status")
    #print(remove_init_sts)

    #print("rename_ig return msg")
    #print(rename_ig)
    #print("rename_ig_sts return status")
    #print(rename_ig_sts)

    #print("rm_ig return msg")
    #print(rm_ig)
    #print("rm_ig_sts return status")
    #print(rm_ig_sts)

    #print("create_cgs return msg")
    #print(create_cg)
    #print("create_cg_sts return status")
    #print(create_cg_sts)

    #print("create_link_cgs return msg")
    #print(refresh_link_cg_dr)
    #print("create_link_cg_sts return status")
    #print(refresh_link_cg_dr_sts)

    #print("refresh_link_cgs return msg")
    #print(refresh_link_cg)
    #print("refresh_link_cg_sts return status")
    #print(refresh_link_cg_sts)

    #print("refresh_link_cgs_mvs return msg")
    #print(refresh_link_cg_msv)
    #print("refresh_link_cg_msv_sts return status")
    #print(refresh_link_cg_msv_sts)

    #print("rename_cg return msg")
    #print(rename_cg)
    #print("rename_cg_sts return status")
    #print(rename_cg_sts)

    #print("rm_cg return msg")
    #print(add_vol_cg)
    #print("rm_cg_sts return status")
    #print(rm_cg_sts)

    #print("add_vol_cg return msg")
    #print(add_vol_cg)
    #print("add_vol_cg_sts return status")
    #print(add_vol_cg_sts)

    #print("na_cg return msg")
    #print(na_cg)
    #print("na_cg_sts return status")
    #print(na_cg_sts)

    #print("rm_vol_cg return msg")
    #print(rm_vol_cg)
    #print("rm_vol_cg_sts return status")
    #print(rm_vol_sts)

    #print("Updated GGS")
    #print([x.get('name') for x in updated_cgs.get('consistency-groups')])

    #print("Updated Initiators")
    #print([x.get('name') for x in updated_inits.get('initiators')])

    #print("ss_info return msg")
    #print(ss_info)
    #print("ss_info_sts return status")
    #print(ss_info_sts)

    #print ("Updated Snapshots")
    #print([x.get('name') for x in updated_ss.get('snapshots')])

    #print("sss_info return msg")
    #print(sss_info)
    #print("sss_info_sts return status")
    #print(sss_info_sts)

    #print("create_ss_cg return msg")
    #print(create_ss_cg)
    #print("create_ss_cg_sts return status")
    #print(create_ss_cg)

    #print("remove_ss_cg return msg")
    #print(remove_ss_cg)
    #print("remove_ss_cg_sts return status")
    #print(remove_ss_cg_sts)

    #print("remove_sss_cg return msg")
    #print(remove_sss_cg)
    #print("remove_ss_cg_sts return status")
    #print(remove_sss_cg_sts)

    #print("Updated Snapshots Sets")
    #print([x.get('name') for x in updated_sss.get('snapshot-sets')])

    #print("tag_info return msg")
    #print(t_info)
    #print("tag_infosts return status")
    #print(t_info_sts)

    #print("create_tag return msg")
    #print(create_tag)
    #print("create_tag_sts return status")
    #print(create_tag_sts)

    #print("rename_tag return msg")
    #print(rename_tag)
    #print("rename_tag_sts return status")
    #print(rename_tag_sts)

    #print("tag_obj return msg")
    #print(tag_obj)
    #print("tag_obj_sts return status")
    #print(tag_obj_sts)

    #print("untag_obj return msg")
    #print(untag_obj)
    #print("untag_obj_sts return status")
    #print(untag_obj_sts)

    #print("rm_tag return msg")
    #print(rm_tag)
    #print("rm_tag_sts return status")
    #print(rm_tag_sts)

    #print("create_lm return msg")
    #pprint.pprint(create_lm)
    #print("create_lm_sts return status")
    #print(create_lm_sts)

    #print("rm_lm return msg")
    #print(rm_map)
    #print("rm_map_sts return status")
    #print(rm_map_sts)

    #print("Updated Tags")
    #print([x.get('name') for x in updated_t.get('tags')])

    #print("Updated Lun Map")
    #print([x.get('name') for x in updated_lm.get('lun-maps')])

    #v_wwn, v_wwn_sts = ru.verify_wwpn("01:23:45:67:89:ab:cd:ef")
    #v_wwn, v_wwn_sts = ru.verify_wwpn("0x0123456789abcdef")
    #v_wwn, v_wwn_sts = ru.verify_wwpn("0123456789abcdef")
    #print(v_wwn)
    #print(v_wwn_sts)

    #obj_sts = ru.does_a_object_exist("SRC2", "volumes", cluster_name)
    #obj_info, obj_sts = ru.do_any_objects_exist(["SRC1", "SRC2"], "volumes", cluster_name)
    #print("MSG: %s | STS: %s" % (obj_info, obj_sts))
    #obj_info, obj_sts = ru.do_all_objects_exist(["SRC11", "SRC22", "SRC21"], "volumes", cluster_name)
    #print("MSG: %s | STS: %s" % (obj_info, obj_sts))

    #sts_msg, sts = ru.is_this_volume_map_to_this_ig("SRC2", "lnx02", cluster_name)
    #print("MSG: %s | STS: %s" % (sts_msg, sts))

    #sts = ru.is_this_volume_map_to_any_igs("SRC1", cluster_name)
    #print("Status Of lun map exist: %s" % sts)

    #sts, _ = ru.get_list_of_igs_map_to_this_volume("test01", cluster_name)
    #print("Status Of lun map exist: %s" % sts)

    #sts_msg, sts = ru.get_list_of_volumes_map_to_this_ig("lnx01")
    #print("MSG: %s | STS: %s" % (sts_msg, sts))

    #sts_msg, sts = ru.create_multiple_volumes("Vest", 1, 2, "5g", cluster_name)
    #print("MSG: %s | STS: %s" % (sts_msg, sts))

    #a="123.12"
    #a_type = ru.verify_var_type(a, dict)
    #a_type = ru.isint(a)
    #print(a_type)
    #input_dict = {"ig_name": 1, "ig_os": "Linux"}
    #def some_func(ig_info):
    #    if (ru.verify_var_type(input_dict, dict)):
    #        if (input_dict["ig_name"]) and ru.verify_var_type(input_dict["ig_name"], str):
    #            print("success")
    #some_func(input_dict)

    #prov_msg, prov_sts = ru.map_new_volumes_to_new_fc_ig("esx45", "esx", ["210261000000021c","210261000000021d"],
    #                                                     "Vol45_", "1", "3", "1g", cluster_name, "cg_esx45")
    #prov_msg, prov_sts = ru.map_new_volumes_to_new_fc_ig("esx45", "esx", 123,
    #                                                     "ESXVol14_", "1", "3", "1g", cluster_name, "cg_esx14")
    #pprint.pprint(prov_msg)
    #print(prov_sts)

    #prov_msg, prov_sts = ru.map_new_volumes_to_existing_fc_ig("esx45", "Vol45_", "10", "3", "1g",
    #                                                          cluster_name, "cg_esx01")
    #prov_msg, prov_sts = ru.map_existing_volumes_to_new_fc_ig("esx55", "esx", ["3002610000000024","3002610000000025"],
    #                                                          ["ESX1_1", "ESX1_2", "ESX1_3"], cluster_name)
    #prov_msg, prov_sts = ru.map_existing_volumes_to_existing_fc_ig("esx02", ["Vest01", "Vest02"], cluster_name, "cg_esx01")


    #pprint.pprint(prov_msg)
    #print(prov_sts)
    #var1 = "Chirag"
    #var2 = 123
    #var3 = ["Patel"]
    #var4 = dict()
    #arg_list = [var1, var2, var3, var4]

    #arg_type_list = [str, int, list, (dict, str)]

    #count = 0
    #while count < len(arg_type_list):
    #    print(type(arg_type_list[count]))
    #    count += 1
    #chk = verify_arguments_types(arg_list, arg_type_list)
    #print()
    #print (chk)













def main():
    get_info()


main()

from PyXtremIO.rest_xtremio import RestFunctions
from PyXtremIO.utils import exception


import unittest
import time
import pytest

username = "admin"
password = "Xtrem10"
hostname = "192.168.86.43"
port = "443"
xioapi_version = "v2"
cluster_name = "xbrick615"

# Test Cases:
# Create objects [vol, init, ig, cg] with and without error checking
# Query same objects [vol, init, ig, cg] with and without error checking
# Rename one of the object [vol, init, ig, cg] with and without error checking
# Rename above object [vol, init, ig, cg] back to original name
# Create snapshots via vol and cg with and without error checking
# Create linked snapshot via cg with and without error checking
# Delete same objects [vol, init, ig, cg] with and without error checking
# Map new ig with new volumes with and without error checking
# Map new volume with existing ig with and without error checking
# Map existing volume with new ig with and without error checking
# Map existing ig with new volumes with and without error checking
# Map existing ig with existing volumes with and without error checking
# Unmap a vol from ig with and without error checking
# Unmap with list of volumes from ig with and without error checking


class TestPyXtremIO(unittest.TestCase):
    def setUp(self):
        self.ru = RestFunctions(username=username, password=password, server_ip=hostname,
                 port=port, xioapi_version=xioapi_version)
        cluster_name = "xbrick615"
        new_vol = "SunVol01"
        new_ig = "sun01"
        new_init = "sun01_hba1"
        new_init_wwpn = "5000000000000001"
        new_cg = "cg_sun01"
        new_tag = "/Volumes/sun01"
        rename_vol = "SunVol02"
        rename_ig = "sun02"
        rename_init = "sun02_hba1"
        rename_cg = "cg_sun02"
        rename_tag = "/Volumes/sun02"

    def test_0001_create_volume_with_syntax_error(self):
        new_vol = "SunVol01"
        # assertRaises calls the function for you. By calling it yourself,
        # the exception is raised before assertRaises can test it. Thus, you can not be successfull with following way
        # of running assertRaises
        # self.assertRaises(exception.VolumeBackendAPIException, self.ru.create_volume(new_vol, "1z", cluster_name))
        # You will need to run following way to be successful.
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.create_volume(new_vol, "1z", cluster_name)

    def test_0002_create_volume_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.create_volume(new_vol, "1g", cluster_name)
        self.assertEqual((type(result_msg), result_sts), (dict, 201))

    def test_0003_increase_volume_size_with_errors(self):
        new_vol = "SunVol01"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.increase_volume_size(new_vol, "500m", cluster_name)

    def test_0004_increase_volume_size_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.increase_volume_size(new_vol, "2g", cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0005_rename_volume_with_errors(self):
        new_vol = "SunVol01"
        rename_vol = "SunVol02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.rename_volume(rename_vol, new_vol, cluster_name)

    def test_0006_rename_volume_without_errors(self):
        new_vol = "SunVol01"
        rename_vol = "SunVol02"
        result_msg, result_sts = self.ru.rename_volume(new_vol, rename_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0007_rename_volume_backtoorgininal_without_errors(self):
        new_vol = "SunVol01"
        rename_vol = "SunVol02"
        result_msg, result_sts = self.ru.rename_volume(rename_vol, new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0008_noaccess_volume_with_errors(self):
        rename_vol = "SunVol02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.enable_noaccess_on_volume(rename_vol, cluster_name)

    def test_0009_noaccess_volume_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.enable_noaccess_on_volume(new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0010_readaccess_volume_with_errors(self):
        rename_vol = "SunVol02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.enable_readaccess_on_volume(rename_vol, cluster_name)

    def test_0011_readaccess_volume_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.enable_readaccess_on_volume(new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0012_writeaccess_volume_with_errors(self):
        rename_vol = "SunVol02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.enable_writeaccess_on_volume(rename_vol, cluster_name)

    def test_0013_writeaccess_volume_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.enable_writeaccess_on_volume(new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0014_enable_mgmtlock_volume_with_errors(self):
        rename_vol = "SunVol02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.enable_mgmtlock_on_volume(rename_vol, cluster_name)

    def test_0015_enable_mgmtlock_volume_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.enable_mgmtlock_on_volume(new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0016_disable_mgmtlock_volume_with_errors(self):
        rename_vol = "SunVol02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.disable_mgmtlock_on_volume(rename_vol, cluster_name)

    def test_0017_disable_mgmtlock_volume_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.disable_mgmtlock_on_volume(new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0018_enable_smio_alert_volume_with_errors(self):
        rename_vol = "SunVol02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.enable_small_io_alert_on_volume(rename_vol, cluster_name)

    def test_0019_enable_smio_alert_volume_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.enable_small_io_alert_on_volume(new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0020_disable_smio_alert_volume_with_errors(self):
        rename_vol = "SunVol02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.disable_small_io_alert_on_volume(rename_vol, cluster_name)

    def test_0021_disable_smio_alert_volume_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.disable_small_io_alert_on_volume(new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0022_enable_unalignedio_alert_volume_with_errors(self):
        rename_vol = "SunVol02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.enable_unaligned_io_alert_on_volume(rename_vol, cluster_name)

    def test_0023_enable_unalignedio_alert_volume_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.enable_unaligned_io_alert_on_volume(new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0024_disable_unalignedio_alert_volume_with_errors(self):
        rename_vol = "SunVol02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.disable_unaligned_io_alert_on_volume(rename_vol, cluster_name)

    def test_0025_disable_unalignedio_alert_volume_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.disable_unaligned_io_alert_on_volume(new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0026_enable_vaaitp_alert_volume_with_errors(self):
        rename_vol = "SunVol02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.enable_vaai_tp_alert_on_volume(rename_vol, cluster_name)

    def test_0027_enable_vaaitp_alert_volume_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.enable_vaai_tp_alert_on_volume(new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0028_disable_vaaitp_alert_volume_with_errors(self):
        rename_vol = "SunVol02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.disable_vaai_tp_alert_on_volume(rename_vol, cluster_name)

    def test_0029_disable_vaaitp_alert_volume_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.disable_vaai_tp_alert_on_volume(new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    ####### Initiators Group #######

    def test_0030_create_initiator_group_without_errors(self):
        new_ig = "sun01"
        result_msg, result_sts = self.ru.create_initiator_group(new_ig, cluster_name)
        self.assertEqual((type(result_msg), result_sts), (dict, 201))

    def test_0031_create_initiator_group_with_errors(self):
        new_ig = "sun01"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.create_initiator_group(new_ig, cluster_name)

    def test_0032_rename_initiator_group_with_errors(self):
        new_ig = "sun01"
        rename_ig = "sun02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.rename_initiator_group(rename_ig, new_ig, cluster_name)

    def test_0033_rename_initiator_group_without_errors(self):
        new_ig = "sun01"
        rename_ig = "sun02"
        result_msg, result_sts = self.ru.rename_initiator_group(new_ig, rename_ig, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0034_rename_initiator_group_without_errors(self):
        new_ig = "sun01"
        rename_ig = "sun02"
        result_msg, result_sts = self.ru.rename_initiator_group(rename_ig, new_ig, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    ####### Initiators #######

    def test_0035_create_initiator_with_errors(self):
        new_init = "sun01_hba1"
        new_init_wwpn = "5000000000000001"
        init_os = "Linux"
        ig_name = "sun01"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.create_initiator(new_init, new_init_wwpn, init_os, ig_name, cluster_name)

    def test_0036_create_initiator_without_errors(self):
        new_init = "sun01_hba1"
        new_init_wwpn = "5000000000000001"
        init_os = "linux"
        ig_name = "sun01"
        result_msg, result_sts = self.ru.create_initiator(new_init, new_init_wwpn, init_os, ig_name, cluster_name)
        self.assertEqual((type(result_msg), result_sts), (dict, 201))

    def test_0037_create_initiator_with_errors(self):
        new_init = "sun01_hba1"
        new_init_wwpn = "5000000000000001"
        init_os = "linux"
        ig_name = "sun01"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.create_initiator(new_init, new_init_wwpn, init_os, ig_name, cluster_name)

    def test_0038_rename_initiator_with_errors(self):
        new_init = "sun01_hba1"
        rename_init = "sun01_HbA2"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.rename_initiator(rename_init, new_init, cluster_name)

    def test_0039_rename_initiator_without_errors(self):
        new_init = "sun01_hba1"
        rename_init = "sun01_HbA2"
        result_msg, result_sts = self.ru.rename_initiator(new_init, rename_init, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0040_rename_initiator_without_errors(self):
        new_init = "sun01_hba1"
        rename_init = "sun01_HbA2"
        result_msg, result_sts = self.ru.rename_initiator(rename_init, new_init, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0041_search_initiator_by_wwpn_with_errors(self):
        new_init_wwpn = "5000000000000002"
        result_msg, result_sts = self.ru.search_initiator_by_wwn(new_init_wwpn, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0042_search_initiator_by_wwpn_without_errors(self):
        new_init_wwpn = "5000000000000001"
        result_msg, result_sts = self.ru.search_initiator_by_wwn(new_init_wwpn)
        self.assertEqual((type(result_msg), result_sts), (dict, 200))

    def test_0043_search_initiator_by_wwpn_without_errors(self):
        new_init_wwpn = "500000000000000101"
        with self.assertRaises(Exception):
            self.ru.search_initiator_by_wwn(new_init_wwpn)

    ### Need to add map & unmap fuctions


    ####### Consistency Group #######

    def test_0043_create_consistency_group_with_errors(self):
        new_cg = "cg_sun01"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.create_consistency_group(1, cluster_name)

    def test_0044_create_consistency_group_without_errors(self):
        new_cg = "cg_sun01"
        result_msg, result_sts = self.ru.create_consistency_group(new_cg, cluster_name)
        self.assertEqual((type(result_msg), result_sts), (dict, 201))

    def test_0045_create_consistency_group_with_errors(self):
        new_cg = "cg_sun01"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.create_consistency_group(new_cg, cluster_name)

    def test_0046_add_volume_consistency_group_with_errors(self):
        new_cg = "cg_sun02"
        new_vol = "SunVol01"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.add_volume_to_consistency_group(new_cg, new_vol, cluster_name)

    def test_0047_add_volume_consistency_group_without_error(self):
        new_cg = "cg_sun01"
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.add_volume_to_consistency_group(new_cg, new_vol, cluster_name)
        self.assertEqual((type(result_msg), result_sts), (dict, 201))

    def test_0048_create_linked_consistency_group_with_errors(self):
        new_cg = "cg_sun02"
        link_cg = "cg_sun01_linked"
        repurpose_flag = "True"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.create_linked_consistency_group(new_cg, link_cg, repurpose_flag, cluster_name,
                                                    new_volume_suffix="linked")

    def test_0049_create_linked_consistency_group_without_errors(self):
        new_cg = "cg_sun01"
        link_cg = "cg_sun01_linked"
        repurpose_flag = "True"
        result_msg, result_sts = self.ru.create_linked_consistency_group(new_cg, link_cg, repurpose_flag, cluster_name,
                                                                         new_volume_suffix="linked")
        self.assertEqual((type(result_msg), result_sts), (dict, 201))

    def test_0050_rename_consistency_group_with_errors(self):
        new_cg = "cg_sun01"
        rename_cg = "cg_sun02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.rename_consistency_group(rename_cg, new_cg, cluster_name)

    def test_0051_rename_consistency_group_without_errors(self):
        new_cg = "cg_sun01"
        rename_cg = "cg_sun02"
        result_msg, result_sts = self.ru.rename_consistency_group(new_cg, rename_cg, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_0052_rename_consistency_group_without_errors(self):
        new_cg = "cg_sun01"
        rename_cg = "cg_sun02"
        result_msg, result_sts = self.ru.rename_consistency_group(rename_cg, new_cg, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))


    ####### Remove Objects #######

    def test_3000_remove_consistency_group_with_errors(self):
        #time.sleep(3)
        new_cg = "cg_sun02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.remove_consistency_group(new_cg, cluster_name)

    def test_3001_remove_consistency_group_without_errors(self):
        new_cg = "cg_sun01"
        result_msg, result_sts = self.ru.remove_consistency_group(new_cg, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_3002_remove_consistency_group_without_errors(self):
        new_cg = "cg_sun01_linked"
        result_msg, result_sts = self.ru.remove_consistency_group(new_cg, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_4000_remove_initiator_with_errors(self):
        new_init = "sun01_hba2"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.remove_initiator(new_init, cluster_name)

    def test_4001_remove_initiator_without_errors(self):
        new_init = "sun01_hba1"
        result_msg, result_sts = self.ru.remove_initiator(new_init, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_5000_remove_initiator_group_with_errors(self):
        new_ig = "sun02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.remove_initiator_group(new_ig, cluster_name)

    def test_5001_remove_initiator_group_without_errors(self):
        new_ig = "sun01"
        result_msg, result_sts = self.ru.remove_initiator_group(new_ig, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_9000_remove_volume_with_errors(self):
        new_vol = "SunVol02"
        with self.assertRaises(exception.VolumeBackendAPIException):
            self.ru.remove_volume(new_vol, cluster_name)

    def test_9001_remove_volume_without_errors(self):
        new_vol = "SunVol01"
        result_msg, result_sts = self.ru.remove_volume(new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    def test_9002_remove_volume_without_errors(self):
        new_vol = "SunVol01.linked"
        result_msg, result_sts = self.ru.remove_volume(new_vol, cluster_name)
        self.assertEqual((result_msg, result_sts), (None, 200))

    #def test_9001_does_a_object_exist_it_does(self):
    #    result = self.ru.does_a_object_exist("SRC2", "volumes", cluster_name)
    #    self.assertEqual(result, True)
    #    print("This is 1.")

    #def test_9002_does_a_object_exist_it_doesnot(self):
    #    result = self.ru.does_a_object_exist("SRC1112", "volumes", cluster_name)
    #    self.assertEqual(result, False)
    #    print("This is 2.")

    #def test_9003_do_all_object_exist(self):
    #    vol_list = ["SRC1", "SRC2", "SRC3"]
    #    result1, result2 = self.ru.do_all_objects_exist(vol_list, "volumes", cluster_name)
    #    self.assertEqual((result1, result2), (None, True))
    #    print("This is 3.")

    #def test_9004_map_existing_volumes_to_existing_fc_ig(self):
    #    vol_list = ["SRC1", "SRC2", "SRC3"]
    #    prov_msg, prov_sts = self.ru.map_existing_volumes_to_existing_fc_ig("esx02", vol_list, cluster_name, "cg_esx01")
    #    self.assertEqual((type(prov_msg), prov_sts), (dict, True))
    #    print("This is 4.")

    def tearDown(self):
        self.ru.close_session()


if __name__ == '__main__':
    unittest.main()
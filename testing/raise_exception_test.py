from PyXtremIO.rest_xtremio import RestFunctions
from PyXtremIO.utils import exception as CE


import unittest
import time
import pytest

username = "admin"
password = "Xtrem10"
hostname = "192.168.86.43"
port = "443"
xioapi_version = "v2"

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

cluster_name = "xbrick615"

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
        rename_ig = "sun02"
        rename_init = "sun02_hba1"
        rename_cg = "cg_sun02"
        rename_tag = "/Volumes/sun02"

    def test_0001_create_volume_with_syntax_error(self):
        new_vol = "SunVol01"
        #result_msg, result_sts = self.ru.create_volume(new_vol, "1z", cluster_name)
        #self.assertRaises(PyXtremIO.utils.exception.VolumeBackendAPIException, self.ru.create_volume(new_vol, "1z", cluster_name))
        self.assertRaises(CE.VolumeBackendAPIException,
                          self.ru.create_volume(new_vol, "1z", cluster_name))
        #self.assertR

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
        print("done")
        self.ru.close_session()
        print("This is 5.")


if __name__ == '__main__':
    unittest.main()
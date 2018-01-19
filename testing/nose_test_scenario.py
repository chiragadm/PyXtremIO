from PyXtremIO.rest_xtremio import RestFunctions
from nose.tools import eq_
import time


cluster_name = "xbrick615"

class TestPyXtremIO():
    def setup(self):
        self.ru = RestFunctions(username="admin", password="Xtrem10", server_ip="192.168.86.43",
                 port="443", xioapi_version='v2')
        cluster_name = "xbrick615"

    def test_does_a_object_exist(self):
        eq_(True, self.ru.does_a_object_exist("SRC2", "volumes", cluster_name))
        eq_(False, self.ru.does_a_object_exist("SRC112", "volumes", cluster_name))
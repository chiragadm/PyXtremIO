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
import csv
import time

try:
    import ConfigParser as Config
except ImportError:
    import configparser as Config
#import logging.config
import six

from PyXtremIO.rest_requests import RestRequests
from PyXtremIO.utils import exception


# register configuration file
#LOG = logging.getLogger('PyXtremIO')
#CONF_FILE = 'PyXtremIO.yaml'
#logging.config.fileConfig(CONF_FILE)
#CFG = Config.ConfigParser()
#CFG.read(CONF_FILE)

# HTTP constants
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'

# PyXtremIO constants
CLUSTERS = 'clusters'
CONSISTENCY_GROUP_VOLUMES = 'consistency-group-volumes'
CONSISTENCY_GROUPS = 'consistency-groups'
INITIATOR_GROUPS = 'initiator-groups'
INITIATORS = 'initiators'
LUN_MAPS = 'lun-maps'
SNAPSHOT_SETS = 'snapshot-sets'
SNAPSHOTS = 'snapshots'
TAGS = 'tags'
VOLUMES = 'volumes'
OBJECT_LIST = ['clusters', 'consistency-group-volumes', 'consistency-groups', 'initiator-groups',
               'initiators', 'lun-maps', 'snapshot-sets', 'snapshots', 'tags', 'volumes']


STATUS_200 = 200
STATUS_201 = 201
STATUS_202 = 202
STATUS_204 = 204
# Job constants
INCOMPLETE_LIST = ['created', 'scheduled', 'running',
                   'validating', 'validated']
CREATED = 'created'
SUCCEEDED = 'succeeded'
CREATE_VOL_STRING = "Creating new Volumes"
ASYNCHRONOUS = "ASYNCHRONOUS"


class RestFunctions:
    def __init__(self, username, password, server_ip,
                 port, verify=False, xioapi_version='v2',
                 interval=5, retries=200):
        self.end_date = int(round(time.time() * 1000))
        self.start_date = (self.end_date - 3600000)
        #self.array_id = CFG.get('setup', 'array')
        if not username:
            username = CFG.get('setup', 'username')
        if not password:
            password = CFG.get('setup', 'password')
        if not server_ip:
            server_ip = CFG.get('setup', 'server_ip')
        if not port:
            port = CFG.get('setup', 'port')
        #if not verify:
        #    verify = CFG.get('setup', 'verify')
        #    if verify.lower() == 'false':
        #        verify = False
        #    elif verify.lower() == 'true':
        #        verify = True
        self.XIOAPI_VERSION = xioapi_version
        base_url = 'https://%s:%s/api/json/%s/types' % (server_ip, port, self.XIOAPI_VERSION)
        self.rest_client = RestRequests(username, password, verify,
                                        base_url)
        self.request = self.rest_client.rest_request
        self.interval = interval
        self.retries = retries

    def verify_arguments_types(self, var_list, arg_list):
        """Verifies input variables matches variable type. This is to avoid potential bugs

        :param var_list: list -- list of argument variables
        :param arg_list: list -- list of above argument variable types in order to the variable reference
                         e.g. if var_list has [var1, var2, var3) then
                         arg_list should have [var1_type, var2_type, var3_type]
                         arg_list also support tuple for two varialbe value type.
                         for example, as above example, var3 can have None or str variable type,
                         your arg_list should be [var1_type, var2_type, (type(None), str)]

        :return: bool
        """
        if len(var_list) != len(arg_list):
            return False
        count = 0
        check_status = True
        while count < len(var_list):
            if type(arg_list[count]) is tuple:
                if type(var_list[count]) is not arg_list[count][0] and type(var_list[count]) is not arg_list[count][1]:
                    check_status = False
            else:
                if type(var_list[count]) != arg_list[count]:
                    check_status = False
            count += 1
        return check_status

    def close_session(self):
        """Close the current rest session
        """
        self.rest_client.close_session()

    def wait_for_job_complete(self, job):
        """Given the job wait for it to complete.

        :param job: the job dict
        :returns: rc -- int, result -- string, status -- string,
                  task -- list of dicts detailing tasks in the job
        :raises: VolumeBackendAPIException
        """
        res, tasks = None, None
        if job['status'].lower() == SUCCEEDED:
            try:
                res, tasks = job['result'], job['task']
            except KeyError:
                pass
            return 0, res, job['status'], tasks

        def _wait_for_job_complete():
            # Called at an interval until the job is finished.
            retries = kwargs['retries']
            try:
                kwargs['retries'] = retries + 1
                if not kwargs['wait_for_job_called']:
                    is_complete, result, rc, status, task = (
                        self._is_job_finished(job_id))
                    if is_complete is True:
                        kwargs['wait_for_job_called'] = True
                        kwargs['rc'], kwargs['status'] = rc, status
                        kwargs['result'], kwargs['task'] = result, task
            except Exception:
                exception_message = "Issue encountered waiting for job."
                LOG.exception(exception_message)
                raise exception.VolumeBackendAPIException(
                    data=exception_message)

            return kwargs

        job_id = job['jobId']
        kwargs = {'retries': 0, 'wait_for_job_called': False,
                  'rc': 0, 'result': None}

        while not kwargs['wait_for_job_called']:
            time.sleep(self.interval)
            kwargs = _wait_for_job_complete()
            if kwargs['retries'] > self.retries:
                LOG.error("_wait_for_job_complete failed after "
                          "%(retries)d tries.", {'retries': kwargs['retries']})
                kwargs['rc'], kwargs['result'] = -1, kwargs['result']
                break

        LOG.debug("Return code is: %(rc)lu. Result is %(res)s.",
                  {'rc': kwargs['rc'], 'res': kwargs['result']})
        return (kwargs['rc'], kwargs['result'],
                kwargs['status'], kwargs['task'])

    def _is_job_finished(self, job_id):
        """Check if the job is finished.

        :param job_id: the id of the job
        :returns: complete -- bool, result -- string,
                  rc -- int, status -- string, task -- list of dicts
        """
        complete, rc, status, result, task = False, 0, None, None, None
        job_url = "/%s/system/job/%s" % (self.XIOAPI_VERSION, job_id)
        job, status_code = self._get_request(job_url, 'job')
        if job:
            status = job['status']
            try:
                result, task = job['result'], job['task']
            except KeyError:
                pass
            if status.lower() == SUCCEEDED:
                complete = True
            elif status.lower() in INCOMPLETE_LIST:
                complete = False
            else:
                rc, complete = -1, True
        return complete, result, rc, status, task

    @staticmethod
    def check_status_code_success(operation, status_code, message):
        """Check if a status code indicates success.

        :param operation: the operation
        :param status_code: the status code
        :param message: the server response
        :raises: VolumeBackendAPIException
        """
        if status_code not in [STATUS_200, STATUS_201,
                               STATUS_202, STATUS_204]:
            exception_message = (
                'Error %(operation)s. The status code received '
                'is %(sc)s and the message is %(message)s.'
                % {'operation': operation,
                   'sc': status_code, 'message': message})
            raise exception.VolumeBackendAPIException(
                data=exception_message)

    def wait_for_job(self, operation, status_code, job):
        """Check if call is async, wait for it to complete.

        :param operation: the operation being performed
        :param status_code: the status code
        :param job: the job
        :returns: task -- list of dicts detailing tasks in the job
        :raises: VolumeBackendAPIException
        """
        task = None
        if status_code == STATUS_202:
            rc, result, status, task = self.wait_for_job_complete(job)
            if rc != 0:
                exception_message = (
                    "Error %(operation)s. Status code: %(sc)lu. "
                    "Error: %(error)s. Status: %(status)s."
                    % {'operation': operation, 'sc': rc,
                       'error': six.text_type(result),
                       'status': status})
                LOG.error(exception_message)
                raise exception.VolumeBackendAPIException(
                    data=exception_message)
        return task

    def _build_uri(self, object_type, object_name=None, version=None):
        """Build the target url.

        :param array: the array serial number
        :param category: the resource category e.g. sloprovisioning
        :param object_type: the resource type e.g. maskingview
        :param object_name: the name of a specific resource
        :param version: the U4V version
        :returns: target url, string
        """
        if version is None:
            version = self.XIOAPI_VERSION
        target_uri = ('/%(object_type)s'
                      % {'object_type': object_type})
        if object_name:
            target_uri += '/?name=%(object_name)s' % {
                'object_name': object_name}
        #if version:
        #    target_uri = ('/%(version)s%(target)s'
        #                  % {'version': version, 'target': target_uri})
        return target_uri

    def _get_request(self, target_uri, object_type, params=None):
        """Send a GET request to the array.

        :param target_uri: the target uri
        :param object_type: the resource type, e.g. maskingview
        :param params: optional dict of filter params
        :returns: resource_object -- dict or None
        """
        resource_object = None
        message, sc = self.request(target_uri, GET, params=params)
        operation = 'get %(res)s' % {'res': object_type}
        try:
            self.check_status_code_success(operation, sc, message)
        except Exception as e:
            LOG.debug("Get resource failed with %(e)s",
                      {'e': e})
        if sc == STATUS_200:
            resource_object = message
        return resource_object, sc

    def get_resource(self, object_type, object_name=None, params=None):
        """Get resource details from array.

        :param object_type: the resource type (e.g. volumes)
        :param object_name: the name of a specific resource (e.g. Vol01)
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        target_uri = self._build_uri(object_type, object_name)
        return self._get_request(target_uri, object_type, params)

    def create_resource(self, object_type, payload):

        """Create a provisioning resource.

        :param object_type: the object type (e.g. volumes)
        :param payload: the payload
        :returns: message -- string, server response, status_code -- int
        """
        target_uri = self._build_uri(object_type)
        message, status_code = self.request(target_uri, POST,
                                            request_object=payload)
        operation = 'Create %(res)s resource' % {'res': object_type}
        self.check_status_code_success(
            operation, status_code, message)
        return message, status_code

    def modify_resource(self, object_type, payload, object_name=None):
        """Modify a resource.

        :param object_type: the object type (e.g. volumes)
        :param payload: the payload
        :param object_name: the object name (e.g. name of volume)
        :returns: message -- string (server response), status_code -- int
        """
        #if version is None:
        #    version = self.XIOAPI_VERSION
        target_uri = self._build_uri(object_type, object_name)
        message, status_code = self.request(target_uri, PUT,
                                            request_object=payload)
        operation = 'modify %(res)s resource' % {'res': object_type}
        self.check_status_code_success(operation, status_code, message)
        return message, status_code

    def delete_resource(self, object_type, object_name, payload=None, params=None):
        """Delete a object of particular object type.

        :param object_type: the type of object to be deleted (e.g. volumes)
        :param object_name: Object name to be deleted (e.g. Vol001)
        :param payload: the payload, optional
        :param params: dict of optional query params
        :returns: message -- string (server response), status_code -- int
        """
        version = self.XIOAPI_VERSION
        target_uri = self._build_uri(object_type, object_name)
        message, status_code = self.request(target_uri, DELETE,
                                            request_object=payload,
                                            params=params, stream=False)
        operation = 'delete %(res)s resource' % {'res': object_type}
        self.check_status_code_success(operation, status_code, message)
        return message, status_code

    def ishex(self, character):
        """Check character for hex string.

        :param character: a single character in string
        :returns: Ture or False
        """
        hex_str = "0123456789abcdefABCDEF"
        if any(character in s for s in hex_str):
            return True
        else:
            return False

    def isint(self, var):
        """Check if variable is int, even if string has number, convert to int

        :param var: input variable
        :return: False or integer
        """
        try:
            int(var)
            return int(var)
        except ValueError:
            return False

    def verify_var_type(self, var, var_type):
        """Check if variable is string

        :param var: input variable
        :param var_type: type of a variable (e.g. int, str, dict, list, set, tuple, float, etc..)
        :return: bool (True or False)
        """
        if type(var) is var_type:
            return True
        else:
            return False

    def convert_wwpn_in_colon_format(self, wwpn):
        """Convert wwpn into long colon format.

        :param character: a single character in string
        :returns: string - XX:XX:XX:XX:XX:XX:XX:XX
        """
        c = ":"
        temp_wwpn = ("%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s" %(wwpn[0], wwpn[1], c, wwpn[2], wwpn[3], c,
                                                                        wwpn[4], wwpn[5], c, wwpn[6], wwpn[7], c,
                                                                        wwpn[8], wwpn[9], c, wwpn[10], wwpn[11], c,
                                                                        wwpn[12], wwpn[13], c, wwpn[14], wwpn[15]))
        return temp_wwpn.lower()

    def verify_wwpn(self, wwpn):
        """Verify WWPN is valid.

        :param wwpn: wwpn of hba in one of the three following format
                     XX:XX:XX:XX:XX:XX:XX:XX
                     XXXXXXXXXXXXXXXX
                     0xXXXXXXXXXXXXXXXX
        :returns: one of the following
                  XX:XX:XX:XX:XX:XX:XX:XX, True
                  "Some error message", False
        """
        if type(wwpn) != str:
            return "wwpn is not string", False
        if len(wwpn) == 23:
            char_count = 1
            for char in wwpn:
                if char_count % 3:
                    if self.ishex(char):
                        pass
                    else:
                        return "wwpn does not have hex character", False
                else:
                    if char != ":":
                        return "wwpn is not valid", False
                char_count += 1
            return wwpn.lower(), True
        elif len(wwpn) == 18:
            if wwpn[0] == "0" and wwpn[1] == "x":
                for char in wwpn[2::]:
                    if self.ishex(char):
                        pass
                    else:
                        return "wwpn does not have hex character", False
            else:
                return "wwpn is not in correct format", False
            new_wwpn = self.convert_wwpn_in_colon_format(wwpn[2::])
            return new_wwpn, True
        elif len(wwpn) == 16:
            for char in wwpn:
                if self.ishex(char):
                    pass
                else:
                    return "wwpn does not have hex character", False
            new_wwpn = self.convert_wwpn_in_colon_format(wwpn)
            return new_wwpn, True
        else:
            return "wwpn has incorrect number of character", False

    @staticmethod
    def create_list_from_file(file_name):
        """Given a file, create a list from its contents.

        :param file_name: the path to the file
        :return: list of contents
        """
        with open(file_name) as f:
            list_item = f.readlines()
        raw_list = map(lambda s: s.strip(), list_item)
        return list(raw_list)

    @staticmethod
    def read_csv_values(file_name):
        """Reads any csv file with headers.

        You can extract the multiple lists from the headers in the CSV file.
        In your own script, call this function and assign to data variable,
        then extract the lists to the variables. Example:
        data=ru.read_csv_values(mycsv.csv)
        sgnamelist = data['sgname']
        policylist = data['policy']
        :param file_name CSV file
        :return: Dictionary of data parsed from CSV
        """
        # open the file in universal line ending mode
        with open(file_name, 'rU') as infile:
            # read the file as a dictionary for each row ({header : value})
            reader = csv.DictReader(infile)
            data = {}
            for row in reader:
                for header, value in row.items():
                    try:
                        data[header].append(value)
                    except KeyError:
                        data[header] = [value]
        return data

    def get_clusters(self, params = None):
        """Get resource details from xtremio cluster.

        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = CLUSTERS
        return self.get_resource(object_type, params)

    def get_initiators(self, cluster_name=None, params=None):
        """Get resource details from array.

        :param cluster_name: the xtremio cluster name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        if cluster_name is None:
            return self.get_resource(object_type, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, params=params_value)

    def get_initiator_info(self, initiator_name, cluster_name=None, params=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a specific object e.g. initiator name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        if cluster_name is None:
            return self.get_resource(object_type, initiator_name, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, initiator_name, params=params_value)

    def create_initiator(self, initiator_name, port_address, os, ig_name, cluster_name, cls_auth_pw=None,
                         cls_auth_user=None, cls_disc_pw=None, cls_disc_user=None, init_auth_pw=None,
                         init_auth_user=None, init_disc_pw=None, init_disc_user=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: Name of initiator
        :param port_address: WWN or INQ name of the port
        :param ig_name: the name of a initiator group
        :param os: Operating System where initiator resides (e.g. Linux, Windows, ESX, Solaris, AIX, HP-UX)
        :param cls_auth_pw: CHAP authentication cluster password
        :param cls_auth_user: CHAP authentication cluster username
        :param cls_disc_pw: CHAP discovery cluster password
        :param cls_disc_user: CHAP discovery cluster username
        :param init_auth_pw: CHAP authentication password
        :param init_auth_user: CHAP authentication username
        :param init_disc_pw: CHAP discovery password
        :param init_disc_user: CHAP discovery Initiator username
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        input_param_dict = {'ig-id': ig_name, 'cluster-id': cluster_name, 'port-address': port_address,
                            'initiator-name': initiator_name, 'operating-system': os,
                            'cluster-authentication-password': cls_auth_pw, 'cluster-authentication-user-name':
                            cls_auth_user, 'cluster-discovery-password': cls_disc_pw, 'cluster-discovery-user-name':
                            cls_disc_user, 'initiator-authentication-password': init_auth_pw,
                            'initiator-authentication-user-name': init_auth_user, 'initiator-discovery-password':
                            init_disc_pw, 'initiator-discovery-user-name': init_disc_user}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def rename_initiator(self, initiator_name, new_initiator_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :param new_initiator_name: new initiator name
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        payload = {'initiator-name': new_initiator_name, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=initiator_name)

    def chg_cls_auth_username_on_initiator(self, initiator_name, new_cls_auth_user, cluster_name):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :param new_cls_auth_user: CHAP authentication cluster username
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        payload = {'cluster-authentication-user-name': new_cls_auth_user, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=initiator_name)

    def chg_cls_disc_pw_on_initiator(self, initiator_name, new_cls_disc_pw, cluster_name):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :param new_cls_disc_pw: CHAP discovery cluster password
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        payload = {'cluster-discovery-password': new_cls_disc_pw, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=initiator_name)

    def chg_cls_disc_user_on_initiator(self, initiator_name, new_cls_disc_user, cluster_name):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :param new_cls_disc_user: CHAP discovery cluster username
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        payload = {'cluster-discovery-user-name': new_cls_disc_user, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=initiator_name)

    def chg_cls_auth_pw_on_initiator(self, initiator_name, new_cls_auth_pw, cluster_name):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :param new_cls_auth_pw: CHAP authentication cluster password
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        payload = {'cluster-authentication-password': new_cls_auth_pw, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=initiator_name)

    def chg_init_auth_pw_on_initiator(self, initiator_name, new_init_auth_pw, cluster_name):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :param new_init_auth_pw: CHAP authentication password
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        payload = {'initiator-authentication-password': new_init_auth_pw, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=initiator_name)

    def chg_init_auth_user_on_initiator(self, initiator_name, new_init_auth_user, cluster_name):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :param new_init_auth_user: CHAP authentication username
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        payload = {'initiator-authentication-user-name': new_init_auth_user, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=initiator_name)

    def chg_init_disc_user_on_initiator(self, initiator_name, new_disc_auth_user, cluster_name):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :param new_disc_auth_user: CHAP discovery username
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        payload = {'initiator-discovery-user-name': new_disc_auth_user, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=initiator_name)

    def chg_init_disc_pw_on_initiator(self, initiator_name, new_disc_auth_pw, cluster_name):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :param new_disc_auth_pw: CHAP discovery password
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        payload = {'initiator-discovery-password': new_disc_auth_pw, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=initiator_name)

    def remove_cls_auth_credentials_on_initiator(self, initiator_name, cluster_name):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        payload = {'remove-cluster-authentication-credentials': "enabled", 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=initiator_name)

    def remove_cls_disc_credentials_on_initiator(self, initiator_name, cluster_name):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        payload = {'remove-cluster-discovery-credentials': "enabled", 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=initiator_name)

    def remove_init_auth_credentials_on_initiator(self, initiator_name, cluster_name):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        payload = {'remove-initiator-authentication-credentials': "enabled", 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=initiator_name)

    def remove_init_disc_credentials_on_initiator(self, initiator_name, cluster_name):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        payload = {'remove-initiator-discovery-credentials': "enabled", 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=initiator_name)

    def remove_initiator(self, initiator_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_name: the name of a initiator
        :returns: resource object -- dict or None
        """
        object_type = INITIATORS
        params_value = ('cluster-name=%(cluster_name)s'
                        % {'cluster_name': cluster_name})
        return self.delete_resource(object_type, object_name=initiator_name, params=params_value)

    def search_initiator_by_wwn(self, initiator_wwn, cluster_name=None, params=None):
        """Search initiator by wwn from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param initiator_wwn: the name of a specific object e.g. initiator wwn in
                              one of the following format (XX:XX:XX:XX:XX:XX:XX:XX,
                              XXXXXXXXXXXXXXXX, 0xXXXXXXXXXXXXXXXX)
        :param params: query parameters
        :returns: One of the following:
                  dict, 200
                  None, 200
        """
        object_type = INITIATORS
        temp_wwn, verify_wwpn_sts = self.verify_wwpn(initiator_wwn)
        if verify_wwpn_sts == True:
            initiator_wwn = temp_wwn
        else:
            raise Exception("Error: %s" % temp_wwn)
        # initiator_wwn_value = ('port_address=%(initiator_wwn)s' % {'initiator_wwn': initiator_wwn})
        if cluster_name is None:
            params_value = ('filter=port_address:eq:%(initiator_wwn)s' % {'initiator_wwn': initiator_wwn})
            tmp_dict, tmp_sc = self.get_resource(object_type, params=params_value)
            if tmp_dict and len(tmp_dict.get('initiators')) != 0:
                # since there is a unique wwpn, only retrieving first initiator name
                initiator_name = tmp_dict.get('initiators')[0].get('name')
                return self.get_initiator_info(initiator_name, params=params)
            else:
                # returning none and original status code since dict / list is empty
                return None, tmp_sc
        else:
            params_value = ('cluster-name=%(cluster_name)s&filter=port_address:eq:%(initiator_wwn)s'
                      % {'cluster_name': cluster_name, 'initiator_wwn': initiator_wwn})
            tmp_dict, tmp_sc = self.get_resource(object_type, params=params_value)
            if tmp_dict and len(tmp_dict.get('initiators')) != 0:
                # since there is a unique wwpn, only retrieving first initiator name
                initiator_name = tmp_dict.get('initiators')[0].get('name')
                return self.get_initiator_info(initiator_name, cluster_name, params)
            else:
                # returning none and original status code since dict / list is empty
                return None, tmp_sc

    def get_initiator_groups(self, cluster_name=None, params=None):
        """Get resource details from array.

        :param cluster_name: the xtremio cluster name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = INITIATOR_GROUPS
        if cluster_name is None:
            return self.get_resource(object_type, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, params=params_value)

    def get_initiator_group_info(self, ig_name, cluster_name=None, params=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param ig_name: the name of a specific object e.g. initiator group name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = INITIATOR_GROUPS
        if cluster_name is None:
            return self.get_resource(object_type, ig_name, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, ig_name, params=params_value)

    def create_initiator_group(self, ig_name, cluster_name, initiator_list=None,
                               tag_list=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param ig_name: the name of a initiator group
        :param initiator_list: This is a list type. List of associated Initiators (name and port number)
        :param tag_list: Tag ID list
        :returns: resource object -- dict or None
        """
        object_type = INITIATOR_GROUPS
        input_param_dict = {'ig-name': ig_name, 'cluster-id': cluster_name,
                            'initiator-list': initiator_list, 'tag-list': tag_list}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def rename_initiator_group(self, ig_name, new_ig_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param ig_name: the name of a initiator group
        :param new_ig_name: new initiator group name
        :returns: resource object -- dict or None
        """
        object_type = INITIATOR_GROUPS
        payload = {'new-name': new_ig_name, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=ig_name)

    def remove_initiator_group(self, ig_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param ig_name: the name of a initiator group
        :returns: resource object -- dict or None
        """
        object_type = INITIATOR_GROUPS
        params_value = ('cluster-name=%(cluster_name)s'
                        % {'cluster_name': cluster_name})
        return self.delete_resource(object_type, object_name=ig_name, params=params_value)

    def get_volumes(self, cluster_name=None, params=None):
        """Get resource details from array.

        :param cluster_name: the xtremio cluster name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        if cluster_name is None:
            return self.get_resource(object_type, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, params=params_value)

    def get_volume_info(self, volume_name, cluster_name=None, params=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param ig_name: the name of a specific object e.g. volume name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        if cluster_name is None:
            return self.get_resource(object_type, volume_name, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, volume_name, params=params_value)

    def create_volume(self, volume_name, volume_size, cluster_name, alignment_offset=None,
                      lb_size=None, small_io_alerts=None, unaligned_io_alert=None,
                      vaai_tp_alert=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a specific object e.g. volume name
        :param volume_size: size of volume (supported format: 10K, 10M, 10G, 10T, 1P)
        :param alignment_offset: The alignment offset for Volumes of 512 LB size is between 0 and 7.
                                 4096 LB volume does not need offset.
        :param lb_size: Logical block size in bytes. Can either be 512 or 4096 bytes.
        :param small_io_alerts: Enable or disable small input/output Alerts.
        :param unaligned_io_alert: Enable or disable unaligned I/O Alerts.
        :param vaai_tp_alert: Enable or disable VAAI TP Alerts.
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES

        input_param_dict = {'vol-name': volume_name, 'vol-size': volume_size, 'cluster-id': cluster_name,
                            'alignment-offset': alignment_offset, 'lb-size': lb_size,
                            'small-io-alerts': small_io_alerts, 'unaligned-io-alerts': unaligned_io_alert,
                            'vaai-tp-alerts': vaai_tp_alert}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def rename_volume(self, volume_name, new_volume_name, cluster_name):
        """Rename volume of xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :param new_volume_name: new volume name
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        payload = {'vol-name': new_volume_name, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=volume_name)

    def increase_volume_size(self, volume_name, new_volume_size, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :param new_volume_size: new volume name
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        payload = {'vol-size': new_volume_size, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=volume_name)

    def enable_small_io_alert_on_volume(self, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        payload = {'small-io-alerts': 'enabled', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=volume_name)

    def disable_small_io_alert_on_volume(self, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        payload = {'small-io-alerts': 'disabled', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=volume_name)

    def enable_unaligned_io_alert_on_volume(self, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        payload = {'unaligned-io-alerts': 'enabled', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=volume_name)

    def disable_unaligned_io_alert_on_volume(self, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        payload = {'unaligned-io-alerts': 'disabled', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=volume_name)

    def enable_vaai_tp_alert_on_volume(self, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        payload = {'vaai-tp-alerts': 'enabled', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=volume_name)

    def disable_vaai_tp_alert_on_volume(self, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        payload = {'vaai-tp-alerts': 'disabled', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=volume_name)

    def enable_noaccess_on_volume(self, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        payload = {'vol-access': 'no_access', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=volume_name)

    def enable_readaccess_on_volume(self, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        payload = {'vol-access': 'read_access', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=volume_name)

    def enable_writeaccess_on_volume(self, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        payload = {'vol-access': 'write_access', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=volume_name)

    def enable_mgmtlock_on_volume(self, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        payload = {'management-locked': 'enabled', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=volume_name)

    def disable_mgmtlock_on_volume(self, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        payload = {'management-locked': 'disabled', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=volume_name)

    def remove_volume(self, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: resource object -- dict or None
        """
        object_type = VOLUMES
        params_value = ('cluster-name=%(cluster_name)s'
                        % {'cluster_name': cluster_name})
        return self.delete_resource(object_type, object_name=volume_name, params=params_value)

    def get_consistency_groups(self, cluster_name=None, params=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = CONSISTENCY_GROUPS
        if cluster_name is None:
            return self.get_resource(object_type, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, params=params_value)

    def get_consistency_group_info(self, cg_name, cluster_name=None, params=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param cg_name: the name of a specific object e.g. consistency group name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = CONSISTENCY_GROUPS
        if cluster_name is None:
            return self.get_resource(object_type, cg_name, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, cg_name, params=params_value)

    def create_consistency_group(self, cg_name, cluster_name, volume_list=None, tag_list=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param cg_name: the name of a consistency group
        :param volume_list: This is a list type. List of volume names
        :param tag_list: Tag ID list
        :returns: resource object -- dict or None
        """
        object_type = CONSISTENCY_GROUPS
        input_param_dict = {'consistency-group-name': cg_name, 'cluster-id': cluster_name,
                            'vol-list': volume_list, 'tag-list': tag_list}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def create_linked_consistency_group(self, from_cg_name, new_cg_name, repurpose_copy_flag, cluster_name,
                                        new_volume_suffix=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param from_cg_name: the name of a source consistency group
        :param new_cg_name: the name of new consistency group
        :param repurpose_copy_flag: The option to create a repurpose copy. Any value triggers
                                    a create of a repurpose copy.
        :param new_volume_suffix: A text string with the new volume suffix.
        :returns: resource object -- dict or None
        """
        object_type = CONSISTENCY_GROUPS
        input_param_dict = {"from-consistency-group-id": from_cg_name, "new-consistency-group-name": new_cg_name,
                            "cluster-id": cluster_name, "repurpose-copy-flag": repurpose_copy_flag,
                            "new-vol-suffix": new_volume_suffix}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def refresh_linked_consistency_group_dryrun(self, from_cg_name, target_cg_name, dry_run, refresh_data, cluster_name,
                                        no_backukp=None):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param from_cg_name: the name of a source consistency group
        :param target_cg_name: the name of target consistency group
        :param dry_run: The option to perform the refresh as a dry-run. A dry-run does not perform the refresh,
                        however the response returns the link information if a refresh were performed.
                        Any value triggers a dry run.
        :param refresh_data: The option to refresh the Consistency Groups or not refresh the Consistency Groups.
                             Any value triggers a refresh.
        :param no_backup: Do not keep backup. Any value triggers this option.
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOTS
        input_param_dict = {"from-consistency-group-id": from_cg_name, "to-consistency-group-id": target_cg_name,
                            "cluster-id": cluster_name, "dry-run": dry_run, "refresh-data": refresh_data,
                            "no-backup": no_backukp}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def refresh_linked_consistency_group(self, from_cg_name, target_cg_name, refresh_data, cluster_name,
                                         no_backup=None, backup_snap_suffix=None, best_effort=None,
                                         snapshot_set_name=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param from_cg_name: the name of a source consistency group
        :param target_cg_name: the name of target consistency group
        :param refresh_data: The option to refresh the Consistency Groups or not refresh the Consistency Groups.
                             Any value triggers a refresh.
        :param no_backup: Do not keep backup. Any value triggers this option.
        :param backup_snap_suffix: String with the backup snapshot suffix.
        :param best_effort: Allows a refresh between group objects, ignoring misaligned volume pairs.
        :param snapshot_set_name: String with the created Snapshot Set Name
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOTS
        input_param_dict = {"from-consistency-group-id": from_cg_name, "to-consistency-group-id": target_cg_name,
                            "cluster-id": cluster_name, "refresh-data": refresh_data,
                            "no-backup": no_backup, "backup-snap-suffix": backup_snap_suffix,
                            "best-effort": best_effort, "snapshot-set-name": snapshot_set_name}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def refresh_linked_consistency_group_ignore_missalign_vols(self, from_cg_name, target_cg_name, ignore_empty_pair,
                                                              refresh_data, cluster_name, no_backukp=None):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param from_cg_name: the name of a source consistency group
        :param target_cg_name: the name of target consistency group
        :param ignore_empty_pair: Indicates whether the request succeeds or fails if either the to volume or from
                                  volume is missing. Values: "true" or "false"
                                  true: Succeed if either the to volume or from volume is missing.
                                  false: Fail if either the to volume or from volume is missing.
        :param refresh_data: The option to refresh the Consistency Groups or not refresh the Consistency Groups.
                             Any value triggers a refresh.
        :param no_backup: Do not keep backup. Any value triggers this option.
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOTS
        input_param_dict = {"from-consistency-group-id": from_cg_name, "to-consistency-group-id": target_cg_name,
                            "cluster-id": cluster_name, "ignore-empty-pair": ignore_empty_pair,
                            "refresh-data": refresh_data, "no-backup": no_backukp}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def rename_consistency_group(self, cg_name, new_cg_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param cg_name: the name of a consistency group
        :param new_cg_name: new consistency group  name
        :returns: resource object -- dict or None
        """
        object_type = CONSISTENCY_GROUPS
        payload = {'new-name': new_cg_name, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=cg_name)

    def remove_consistency_group(self, cg_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param cg_name: the name of a consistency group
        :returns: resource object -- dict or None
        """
        object_type = CONSISTENCY_GROUPS
        params_value = ('cluster-name=%(cluster_name)s'
                        % {'cluster_name': cluster_name})
        return self.delete_resource(object_type, object_name=cg_name, params=params_value)

    def add_volume_to_consistency_group(self, cg_name, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param cg_name: the name of a  consistency group
        :param volume_name: the name of volume
        :returns: resource object -- dict or None
        """
        object_type = CONSISTENCY_GROUP_VOLUMES
        input_param_dict = {"cg-id": cg_name, "vol-id": volume_name, "cluster-id": cluster_name}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def add_paired_volume_to_consistency_group(self, cg_name, volume_name, reference_volume_name,  cluster_name):
        # TODO: Need to test this function.
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param cg_name: the name of a  consistency group
        :param volume_name: the name of volume
        :param reference_volume_name: The ID of the reference volume used to allow adding a volume with existing copy
                                      relationships.
        :returns: resource object -- dict or None
        """
        object_type = CONSISTENCY_GROUP_VOLUMES
        input_param_dict = {"cg-id": cg_name, "vol-id": volume_name, "cluster-id": cluster_name,
                            "reference-volume- id": reference_volume_name}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def enable_noaccess_on_consistency_group(self, cg_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param cg_name: the name of a consistency group
        :returns: resource object -- dict or None
        """
        object_type = CONSISTENCY_GROUP_VOLUMES
        payload = {'vol-access': 'no_access', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=cg_name)

    def enable_readaccess_on_consistency_group(self, cg_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param cg_name: the name of a consistency group
        :returns: resource object -- dict or None
        """
        object_type = CONSISTENCY_GROUP_VOLUMES
        payload = {'vol-access': 'read_access', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=cg_name)

    def enable_writeaccess_on_consistency_group(self, cg_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param cg_name: the name of a consistency group
        :returns: resource object -- dict or None
        """
        object_type = CONSISTENCY_GROUP_VOLUMES
        payload = {'vol-access': 'write_access', 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=cg_name)

    def remove_volume_from_consistency_group(self, cg_name, volume_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param cg_name: the name of a consistency group
        :param volume_name: the name of a volume
        :returns: resource object -- dict or None
        """
        object_type = CONSISTENCY_GROUP_VOLUMES
        payload = {'cg-id': cg_name, 'vol-id': volume_name, 'cluster-id': cluster_name}
        return self.delete_resource(object_type, cg_name, payload)

    def get_snapshots(self, cluster_name=None, params=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOTS
        if cluster_name is None:
            return self.get_resource(object_type, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, params=params_value)

    def get_snapshot_info(self, ss_name, cluster_name=None, params=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param ss_name: the name of a specific object e.g. snapshot name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOTS
        if cluster_name is None:
            return self.get_resource(object_type, ss_name, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, ss_name, params=params_value)

    def create_snapshot_from_consistency_group(self, cg_name, cluster_name, snapshot_set_name=None, snap_suffix=None,
                                               snapshot_type=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param cg_name: the name of a consistency group
        :param snapshot_set_name: The name of the Snapshot Set
        :param snap_suffix: A string added after a Snapshot stem name, limited to 64 characters
        :param snapshot_type: The Snapshot is read/write (default) or read-only.
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOTS
        input_param_dict = {"consistency-group-id": cg_name, "snapshot-set-name": snapshot_set_name,
                            "cluster-id": cluster_name, "snap-suffix": snap_suffix, "snapshot-type": snapshot_type}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def create_snapshot_from_snapshot_set_name(self, orig_snapshot_set_name, cluster_name, snapshot_set_name=None,
                                               snap_suffix=None, snapshot_type=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param orig_snapshot_set_name: the name of a original snapshot set name
        :param snapshot_set_name: The name of the Snapshot Set
        :param snap_suffix: A string added after a Snapshot stem name, limited to 64 characters
        :param snapshot_type: The Snapshot is read/write (default) or read-only.
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOTS
        input_param_dict = {"snapshot-set-id": orig_snapshot_set_name, "snapshot-set-name": snapshot_set_name,
                            "cluster-id": cluster_name, "snap-suffix": snap_suffix, "snapshot-type": snapshot_type}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def create_snapshot_from_volumelist(self, volume_list, cluster_name, snapshot_set_name=None, snap_suffix=None,
                                        snapshot_type=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_list: list of volumes. This should be list variable. (e.g. ["Vol1", "Vol2"]
        :param snapshot_set_name: The name of the Snapshot Set
        :param snap_suffix: A string added after a Snapshot stem name, limited to 64 characters
        :param snapshot_type: The Snapshot is read/write (default) or read-only.
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOTS
        input_param_dict = {"volume-list": volume_list, "snapshot-set-name": snapshot_set_name,
                            "cluster-id": cluster_name, "snap-suffix": snap_suffix, "snapshot-type": snapshot_type}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def create_snapshot_from_taglist(self, tag_list, cluster_name, snapshot_set_name=None, snap_suffix=None,
                                     snapshot_type=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param tag_list: list of volumes. This should be list variable. (e.g. ["Vol1", "Vol2"]
        :param snapshot_set_name: The name of the Snapshot Set
        :param snap_suffix: A string added after a Snapshot stem name, limited to 64 characters
        :param snapshot_type: The Snapshot is read/write (default) or read-only.
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOTS
        input_param_dict = {"tag-list": tag_list, "snapshot-set-name": snapshot_set_name,
                            "cluster-id": cluster_name, "snap-suffix": snap_suffix, "snapshot-type": snapshot_type}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def remove_snapshot(self, snapshot_vol_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param snapshot_vol_name: the name of a snapshot volume name
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOTS
        params_value = ('cluster-name=%(cluster_name)s'
                        % {'cluster_name': cluster_name})
        return self.delete_resource(object_type, object_name=snapshot_vol_name, params=params_value)

    def get_snapshot_sets(self, cluster_name=None, params=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOT_SETS
        if cluster_name is None:
            return self.get_resource(object_type, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, params=params_value)

    def get_snapshot_set_info(self, ss_set_name, cluster_name=None, params=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param ss_set_name: the name of a specific object e.g. snapshot set name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOT_SETS
        if cluster_name is None:
            return self.get_resource(object_type, ss_set_name, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, ss_set_name, params=params_value)

    def rename_snapshot_set(self, ss_set_name, new_ss_set_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param ss_set_name: the name of a snapshot set
        :param new_ss_set_name: new snapshot set name
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOT_SETS
        payload = {'new-name': new_ss_set_name, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=ss_set_name)

    def remove_snapshot_set(self, ss_set_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param ss_set_name: the name of a snapshot set
        :returns: resource object -- dict or None
        """
        object_type = SNAPSHOT_SETS
        params_value = ('cluster-name=%(cluster_name)s'
                        % {'cluster_name': cluster_name})
        return self.delete_resource(object_type, object_name=ss_set_name, params=params_value)

    def get_tags(self, cluster_name=None, params=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = TAGS
        if cluster_name is None:
            return self.get_resource(object_type, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, params=params_value)

    def get_tag_info(self, tag_name, cluster_name=None, params=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param tag_name: the name of a tag
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = TAGS
        if cluster_name is None:
            return self.get_resource(object_type, tag_name, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, tag_name, params=params_value)

    def create_tag(self, entity, tag_name):
        """Get resource details from xtremio cluster.

        :param tag_name: the name of a tag
        :param entity: The entity type associated (InfinibandSwitch, DAE, Initiator, BatteryBackupUnit, Scheduler,
                       StorageController, DataProtectionGroup, X-Brick, Volume, Cluster, InitiatorGroup, SSD,
                       SnapshotSet, ConsistencyGroup, Target)
        :returns: resource object -- dict or None
        """
        object_type = TAGS
        input_param_dict = {"entity": entity, "tag-name": tag_name}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def rename_tag(self, orig_tag_name, new_tag_name):
        """Get resource details from xtremio cluster.

        :param orig_tag_name: the name of a tag (.e.g /Volume/Prod)
        :param new_tag_name: new tag name (e.g. Test) (No /Volume required as per above example)
        :returns: resource object -- dict or None
        """
        object_type = TAGS
        payload = {'caption': new_tag_name}
        return self.modify_resource(object_type, payload, object_name=orig_tag_name)

    def tag_object(self, object_name, tag_name, entity, cluster_name):
        """Get resource details from xtremio cluster.

        :param tag_name: the name of a tag (.e.g /Volume/Prod)
        :param object_name: new of a object (e.g name of a Volume)
        :param entity: Name of an entity (e.g Volume)
        :returns: resource object -- dict or None
        """
        object_type = TAGS
        payload = {'entity-details': object_name, 'entity': entity, 'cluster-id': cluster_name}
        return self.modify_resource(object_type, payload, object_name=tag_name)

    def untag_object(self, object_name, tag_name, entity, cluster_name):
        """Get resource details from xtremio cluster.

        :param tag_name: the name of a tag (.e.g /Volume/Prod)
        :param object_name: new of a object (e.g name of a Volume)
        :param entity: Name of an entity (e.g Volume)
        :returns: resource object -- dict or None
        """
        object_type = TAGS
        payload = {'entity-details': object_name, 'entity': entity, 'cluster-id': cluster_name}
        return self.delete_resource(object_type, tag_name, payload)

    def remove_tag(self, tag_name):
        """Get resource details from xtremio cluster.

        :param tag_name: the name of a tag
        :returns: resource object -- dict or None
        """
        object_type = TAGS
        #params_value = ('cluster-name=%(cluster_name)s'
        #                % {'cluster_name': cluster_name})
        #return self.delete_resource(object_type, object_name=tag_name, params=params_value)
        return self.delete_resource(object_type, object_name=tag_name)

    def get_lun_map(self, cluster_name=None, params=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = LUN_MAPS
        if cluster_name is None:
            return self.get_resource(object_type, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, params=params_value)

    def get_lun_map_info(self, map_name, cluster_name=None, params=None):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param map_name: the name of a amp
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        object_type = LUN_MAPS
        if cluster_name is None:
            return self.get_resource(object_type, map_name, params=params)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                      % {'cluster_name': cluster_name})
            return self.get_resource(object_type, map_name, params=params_value)

    def is_this_volume_map_to_this_ig(self, volume_name, ig_name, cluster_name=None):
        """Search initiator by wwn from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :param ig_name: the name of a initiator group
        :returns: One of the following
                  map name, True
                  None, False
        """
        object_type = LUN_MAPS
        if cluster_name is None:
            params_value = ('filter=vol-name:eq:%(volume_name)s&filter=ig-name:eq:%(ig_name)s' %
                            {'volume_name': volume_name, 'ig_name': ig_name})
            tmp_dict, tmp_sc = self.get_resource(object_type, params=params_value)
            if tmp_dict and len(tmp_dict.get('lun-maps')) != 0:

                return tmp_dict['lun-maps'][0]['name'], True
            else:
                return None, False
        else:
            params_value = ('cluster-name=%(cluster_name)s&filter=vol-name:eq:%(volume_name)s'
                            '&filter=ig-name:eq:%(ig_name)s' % {'cluster_name': cluster_name,
                                                                'volume_name': volume_name, 'ig_name': ig_name})
            tmp_dict, tmp_sc = self.get_resource(object_type, params=params_value)
            if tmp_dict and len(tmp_dict.get('lun-maps')) != 0:
                return tmp_dict['lun-maps'][0]['name'], True
            else:
                return None, False

    def is_this_volume_map_to_any_igs(self, volume_name, cluster_name=None):
        """Search initiator by wwn from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: bool (True or False)
        """
        object_type = LUN_MAPS
        if cluster_name is None:
            params_value = ('filter=vol-name:eq:%(volume_name)s' %
                            {'volume_name': volume_name})
            tmp_dict, tmp_sc = self.get_resource(object_type, params=params_value)
            if tmp_dict and len(tmp_dict.get('lun-maps')) != 0:
                return True
            else:
                return False
        else:
            params_value = ('cluster-name=%(cluster_name)s&filter=vol-name:eq:%(volume_name)s'
                            % {'cluster_name': cluster_name, 'volume_name': volume_name})
            tmp_dict, tmp_sc = self.get_resource(object_type, params=params_value)
            if tmp_dict and len(tmp_dict.get('lun-maps')) != 0:
                return True
            else:
                return False

    def get_list_of_igs_map_to_this_volume(self, volume_name, cluster_name=None):
        """Search initiator by wwn from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param volume_name: the name of a volume
        :returns: One of the following option
                  None, False
                  List of initiator group name, True
        """
        object_type = LUN_MAPS
        if cluster_name is None:
            params_value = ('filter=vol-name:eq:%(volume_name)s' %
                            {'volume_name': volume_name})
            tmp_dict, tmp_sc = self.get_resource(object_type, params=params_value)
            if tmp_dict and len(tmp_dict.get('lun-maps')) != 0:
                ig_list = list()
                for ig_item in tmp_dict.get('lun-maps'):
                    ig_temp, _ = self.get_lun_map_info(ig_item.get('name'))
                    ig_list.append(ig_temp.get('content').get('ig-name'))
                return ig_list, True
            else:
                return None, False
        else:
            params_value = ('cluster-name=%(cluster_name)s&filter=vol-name:eq:%(volume_name)s'
                            % {'cluster_name': cluster_name, 'volume_name': volume_name})
            tmp_dict, tmp_sc = self.get_resource(object_type, params=params_value)
            if tmp_dict and len(tmp_dict.get('lun-maps')) != 0:
                ig_list = list()
                for ig_item in tmp_dict.get('lun-maps'):
                    ig_temp, _ = self.get_lun_map_info(ig_item.get('name'), cluster_name)
                    ig_list.append(ig_temp.get('content').get('ig-name'))
                return ig_list, True
            else:
                return None, False

    def get_list_of_volumes_map_to_this_ig(self, ig_name, cluster_name=None):
        """Search initiator by wwn from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param ig_name: the name of a initiator name
        :returns: One of the following option
                  None, False
                  List of volume name, True
        """
        object_type = LUN_MAPS
        if cluster_name is None:
            params_value = ('filter=ig-name:eq:%(ig_name)s' %
                            {'ig_name': ig_name})
            tmp_dict, tmp_sc = self.get_resource(object_type, params=params_value)
            if tmp_dict and len(tmp_dict.get('lun-maps')) != 0:
                vol_list = list()
                for map_item in tmp_dict.get('lun-maps'):
                    vol_temp, _ = self.get_lun_map_info(map_item.get('name'))
                    vol_list.append(vol_temp.get('content').get('vol-name'))
                return vol_list, True
            else:
                return None, False
        else:
            params_value = ('cluster-name=%(cluster_name)s&filter=ig-name:eq:%(ig_name)s'
                            % {'cluster_name': cluster_name, 'ig_name': ig_name})
            tmp_dict, tmp_sc = self.get_resource(object_type, params=params_value)
            if tmp_dict and len(tmp_dict.get('lun-maps')) != 0:
                vol_list = list()
                for map_item in tmp_dict.get('lun-maps'):
                    vol_temp, _ = self.get_lun_map_info(map_item.get('name'), cluster_name)
                    vol_list.append(vol_temp.get('content').get('vol-name'))
                return vol_list, True
            else:
                return None, False
            #return tmp_dict, tmp_sc

    def create_lun_map(self, volume_name, ig_name, cluster_name, target_group_name=None, hlu=None):
        """Get resource details from xtremio cluster.

        :param target_group_name: the name of a target group
        :param volume_name: the name of a volume (e.g. Vol01)
        :param ig_name: the name of a initiator group (e.g. IG_LNX01)
        :param cluster_name: the name of xtremio cluster
        :param hlu: Lun id expose to host. It is int type.
        :returns: dict or None, status_code -- int
        """
        object_type = LUN_MAPS
        input_param_dict = {"vol-id": volume_name, "ig-id": ig_name, "cluster-id": cluster_name,
                            "tg-id": target_group_name, "lun": hlu}
        payload = dict()
        for key, value in input_param_dict.items():
            if value:
                payload.update({key: value})
        return self.create_resource(object_type, payload)

    def unmap_volume_from_ig(self, volume_name, ig_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param ig_name: the name of a initiator group
        :param volume_name: the name of volume
        :returns: one of the following
                  string - Error message, False
                  None, True
        """
        var_list = [volume_name, ig_name, cluster_name]
        arg_list = [str, str, str]
        if self.verify_arguments_types(var_list, arg_list) is False:
            err_msg = "Error: one of more function input type is wrong. Please verify your input."
            return err_msg, False
        object_type = LUN_MAPS
        map_name, map_sts = self.is_this_volume_map_to_this_ig(volume_name, ig_name, cluster_name)
        if map_sts is True:
            params_value = ('cluster-name=%(cluster_name)s'
                        % {'cluster_name': cluster_name})
            _, _ = self.delete_resource(object_type, object_name=map_name, params=params_value)
            return None, True
        else:
            err_msg = ("Error: Mapping does exist between volume %s and initiator %s on %s cluster or "
                       "these object does not exists" % (volume_name, ig_name, cluster_name))
            return err_msg, False

    def unmap_multiple_volumes_from_ig(self, volume_list, ig_name, cluster_name):
        """Get resource details from xtremio cluster.

        :param cluster_name: the xtremio cluster name
        :param ig_name: the name of a initiator group
        :param volume_list: list of volume names (e.g. ["Vol01", "Vol02"])
        :returns: one of the following
                  string - Error message, False
                  None, True
        """
        var_list = [volume_list, ig_name, cluster_name]
        arg_list = [list, str, str]
        if self.verify_arguments_types(var_list, arg_list) is False:
            err_msg = "Error: one of more function input type is wrong. Please verify your input."
            return err_msg, False
        object_type = LUN_MAPS
        volume_list_is_list = self.verify_var_type(volume_list, list)
        if volume_list_is_list is False:
            err_msg = "Error: Volume list input is not a list type. Please correct the input."
            return err_msg, False
        map_doesnot_exist = False
        map_doesnot_exist_list = list()
        map_list = list()
        for volume_name in volume_list:
            map_name, map_sts = self.is_this_volume_map_to_this_ig(volume_name, ig_name, cluster_name)
            if map_sts is False:
                map_doesnot_exist = True
                map_doesnot_exist_list.append(volume_name)
            else:
                map_list.append(map_name)
        if map_doesnot_exist is True:
            err_msg = ("Error: Mapping does exist between volume %s and initiator %s on %s cluster or "
                       "these object does not exists" % (map_doesnot_exist_list, ig_name, cluster_name))
            return err_msg, False
        for map_name in map_list:
            params_value = ('cluster-name=%(cluster_name)s'
                        % {'cluster_name': cluster_name})
            _, _ = self.delete_resource(object_type, object_name=map_name, params=params_value)
        return None, True

    def get_object_list(self, object_type, cluster_name=None):
        """Verify if object name exist in xtremio cluster.

        :param object_type: the type of object (e.g. volumes)
        :param cluster_name: the name of xtremio cluster
        :returns: list of object_names or False
        """
        if cluster_name is None:
            object_info, _ = self.get_resource(object_type, params=None)
        else:
            params_value = ('cluster-name=%(cluster_name)s'
                            % {'cluster_name': cluster_name})
            object_info, _ = self.get_resource(object_type, params=params_value)
        if object_info is None:
            return False
        else:
            return [x.get('name') for x in object_info.get(object_type)]

    def does_a_object_exist(self, object_name, object_type, cluster_name=None):
        """Verify if object name exist in xtremio cluster.

        :param object_name: the name of a object (e.g. Vol1)
        :param object_type: the type of object (e.g. volumes)
        :param cluster_name: the name of xtremio cluster
        :returns: bool (Ture or False)
        """
        object_exist = False
        object_list = self.get_object_list(object_type, cluster_name)
        if object_list is not False:
            if any(object_name in object_item for object_item in object_list):
                object_exist = True
        return object_exist

    def do_any_objects_exist(self, object_name_list, object_type, cluster_name=None):
        """Verify if object name exist in xtremio cluster.

        :param object_name_list: list of object names (e.g. ["Vol1", "Vol2"])
        :param object_type: the type of object (e.g. volumes)
        :param cluster_name: the name of xtremio cluster
        :returns: one of the following
                  list of object name that exists, Ture
                  None, False
        """
        object_exist = False
        object_list = self.get_object_list(object_type, cluster_name)
        if object_list is not False:
            object_item_list = list()
            for object_name in object_name_list:
                if any(object_name in object_item for object_item in object_list):
                    object_exist = True
                    object_item_list.append(object_name)
            if object_exist is True:
                return object_item_list, object_exist
            else:
                return None, object_exist
        else:
            return None, object_exist

    def do_all_objects_exist(self, object_name_list, object_type, cluster_name=None):
        """Verify if object name exist in xtremio cluster.

        :param object_name_list: list of object names (e.g. ["Vol1", "Vol2"])
        :param object_type: the type of object (e.g. volumes)
        :param cluster_name: the name of xtremio cluster
        :returns: one of the following
                  None, Ture
                  list of object name that does not exist, False
                  None, False
        """
        object_exist = False
        object_list = self.get_object_list(object_type, cluster_name)
        if object_list is not False:
            object_item_list = list()
            for object_name in object_name_list:
                if any(object_name in object_item for object_item in object_list):
                    object_item_list.append(object_name)
            if object_name_list == object_item_list:
                return None, True
            else:
                return list(set(object_item_list).symmetric_difference(set(object_name_list))), object_exist
        else:
            return None, object_exist

    def create_multiple_volumes(self, volume_prefix_name, volume_suffix_count,
                                num_of_volume, volume_size, cluster_name):
        """

        :param volume_prefix_name: string - Name of a volume prefix (e.g. Vol)
        :param volume_suffix_count: int - starting integer for suffix (e.g. 1)
        :param num_of_volume: int - number of volumes that need to be created (e.g. 5)
        :param volume_size: string - size of volume (supported format: 10K, 10M, 10G, 10T, 1P)
        :param cluster_name: string - the name of a cluster
        :return: one of the following
                 Error String, False
                 List of volumes names, True
        """
        var_list = [volume_prefix_name, volume_suffix_count, num_of_volume, volume_size, cluster_name]
        arg_list = [str, (int, str), (int, str), str, str]
        if self.verify_arguments_types(var_list, arg_list) is False:
            err_msg = "Error: one of more function input type is wrong. Please verify your input."
            return err_msg, False
        volume_suffix_count = self.isint(volume_suffix_count)
        num_of_volume = self.isint(num_of_volume)
        if type(volume_suffix_count) is not int or type(num_of_volume) is not int:
            raise Exception("Error: volume_suffix_count or num_of_volume is not integer")
        vol_list = list()
        temp_count = 0
        while temp_count < num_of_volume:
            vol_list.append("%s%.2d" % (volume_prefix_name, volume_suffix_count))
            volume_suffix_count += 1
            temp_count += 1
        verify_vol_exist, verify_vol_exist_sts = self.do_any_objects_exist(vol_list, "volumes", cluster_name)
        if verify_vol_exist_sts is True:
            err_msg = ("These volume already exists on cluster %s: %s" % (cluster_name, verify_vol_exist))
            return err_msg, False
        else:
            for vol in vol_list:
                _, _ = self.create_volume(vol, volume_size, cluster_name)
            return vol_list, True

    def map_new_volumes_to_new_fc_ig(self, ig_name, ig_os, wwpn_list, volume_prefix_name, volume_suffix_count,
                                     num_of_volumes, volume_size, cluster_name, cg_name=None):
        """Create new volumes and initiator group and map them.

        :param ig_name: string - the name of initiator group (e.g. ServerName)
        :param ig_os: string - Operating System where initiator group resides (e.g. one of the following option
                      [solaris, aix, windows, esx, other, linux, hpux]
        :param wwpn_list: list - list of initiator's wwpn
        :param volume_prefix_name: string - Name of a volume prefix (e.g. Vol)
        :param volume_suffix_count: int - starting integer for suffix (e.g. 1)
        :param num_of_volumes: int - number of volumes that need to be created (e.g. 5)
        :param volume_size: string - size of volume (supported format: 10K, 10M, 10G, 10T, 1P)
        :param cluster_name: string - the name of a cluster
        :param cg_name: string - the name of a consistency group
        :return: one of the following two:
                 string - some error msg, False
                 dict, True
                 Dict will be like following:
                 {'consistency-group-name': 'cg_esx01',
                    'ig-name': 'esx01',
                    'initiators-info': [{'initiator-name': 'esx01_HBA01',
                                      'operating-system': 'esx',
                                      'port-address': '200261000000001c'}],
                    'volumes-info': [{'naa-name': 'c0c5d38bfa22f054',
                                      'vol-name': 'ESXVol01',
                                      'vol-size': '1048576'}]
                 }
        """
        var_list = [ig_name, ig_os, wwpn_list, volume_prefix_name, volume_suffix_count, num_of_volumes, volume_size,
                    cluster_name, cg_name]
        arg_list = [str, str, list, str, (int, str), (int, str), str, str, (type(None), str)]
        if self.verify_arguments_types(var_list, arg_list) is False:
            err_msg = "Error: one of more function input type is wrong. Please verify your input."
            return err_msg, False
        object_exist_status = False
        if self.does_a_object_exist(ig_name, "initiator-groups", cluster_name) is True:
            object_exist_status = True
        for init_wwpn in wwpn_list:
            init_wwn_sts, _ = self.search_initiator_by_wwn(init_wwpn, cluster_name)
            if init_wwn_sts is not None:
                object_exist_status = True
        init_count = 1
        for init_wwpn in wwpn_list:
            init_name = ("%s_HBA%.2d" % (ig_name, init_count))
            if self.does_a_object_exist(init_name, "initiators", cluster_name) is True:
                object_exist_status = True
            init_count += 1
        if ig_os not in ["solaris", "aix", "windows", "esx", "other", "linux", "hpux"]:
            err_msg = ("initiator os is %s. however, it only excepts [solaris, aix, windows, esx, other, linux, hpux] "
                       "values" % ig_os)
            return err_msg, False
        vol_creation, vol_creation_sts = self.create_multiple_volumes(volume_prefix_name, volume_suffix_count,
                                                                      num_of_volumes, volume_size, cluster_name)
        if vol_creation_sts is False:
            object_exist_status = True
        if object_exist_status is True:
            err_msg = "Error: initiator group, wwpn or volume name already exists, please verify your inputs"
            return err_msg, False
        return_dict = dict()
        _, _ = self.create_initiator_group(ig_name, cluster_name)
        return_dict['ig-name'] = ig_name
        init_return_list = list()
        init_count = 1
        for init_wwpn in wwpn_list:
            init_name = ("%s_HBA%.2d" % (ig_name, init_count))
            _, _ = self.create_initiator(init_name, init_wwpn, ig_os, ig_name, cluster_name)
            init_return_list.append({'initiator-name': init_name, 'port-address': init_wwpn, 'operating-system': ig_os})
            init_count += 1
        return_dict['initiators-info'] = init_return_list
        for vol in vol_creation:
            vol_msg, _ = self.create_lun_map(vol, ig_name, cluster_name)
        if cg_name:
            if self.does_a_object_exist(cg_name, "consistency-groups", cluster_name) is True:
                for vol in vol_creation:
                    _, _ = self.add_volume_to_consistency_group(cg_name, vol, cluster_name)
                return_dict['consistency-group-name'] = cg_name
            else:
                _, _ = self.create_consistency_group(cg_name, cluster_name, vol_creation)
                return_dict['consistency-group-name'] = cg_name
        vol_return_list = list()
        #time.sleep(12)
        #for vol in vol_creation:
        #    t_vol, _ = self.get_volume_info(vol, cluster_name)
        #    vol_naa = t_vol.get('content').get('naa-name')
        #    v_size = t_vol.get('content').get('vol-size')
        #    vol_return_list.append({'vol-name': vol, 'vol-size': v_size, 'naa-name': vol_naa})
        #return_dict['volumes-info'] = vol_return_list
        #return return_dict, True
        # Following code is ensure that if vol_naa is "" then it will try to get naa till it is not "" or try to
        # 15 sec.
        wait_count = 0
        wait_times = 30
        for vol in vol_creation:
            while wait_count < wait_times:
                t_vol, _ = self.get_volume_info(vol, cluster_name)
                vol_naa = t_vol.get('content').get('naa-name')
                if vol_naa != "":
                    wait_count = wait_times + 1
                wait_count += 1
                time.sleep(.5)
            v_size = t_vol.get('content').get('vol-size')
            vol_return_list.append({'vol-name': vol, 'vol-size': v_size, 'naa-name': vol_naa})
        return_dict['volumes-info'] = vol_return_list
        return return_dict, True

    def map_new_volumes_to_existing_fc_ig(self, ig_name, volume_prefix_name, volume_suffix_count,
                                     num_of_volumes, volume_size, cluster_name, cg_name=None):
        """Create new volumes and initiator group and map them.

        :param ig_name: string - the name of initiator group (e.g. ServerName)
        :param volume_prefix_name: string - Name of a volume prefix (e.g. Vol)
        :param volume_suffix_count: int - starting integer for suffix (e.g. 1)
        :param num_of_volumes: int - number of volumes that need to be created (e.g. 5)
        :param volume_size: string - size of volume (supported format: 10K, 10M, 10G, 10T, 1P)
        :param cluster_name: string - the name of a cluster
        :param cg_name: string - the name of consistency group
        :return: one of the following two:
                 string - some error msg, False
                 dict, True
                 Dict will be like following:
                 {'consistency-group-name': 'cg_esx01',
                    'ig-name': 'esx01',
                    'initiators-info': [{'initiator-name': 'esx01_HBA01',
                                      'operating-system': 'esx',
                                      'port-address': '200261000000001c'}],
                    'volumes-info': [{'naa-name': 'c0c5d38bfa22f054',
                                      'vol-name': 'ESXVol01',
                                      'vol-size': '1048576'}]
                 }
        """
        var_list = [ig_name, volume_prefix_name, volume_suffix_count, num_of_volumes, volume_size, cluster_name, cg_name]
        arg_list = [str, str, (int, str), (int, str), str, str, (type(None), str)]
        if self.verify_arguments_types(var_list, arg_list) is False:
            err_msg = "Error: one of more function input type is wrong. Please verify your input."
            return err_msg, False
        object_exist_status = False
        return_dict = dict()
        if self.does_a_object_exist(ig_name, "initiator-groups", cluster_name) is not True:
            object_exist_status = True
        init_return_list = list()
        params_value = ('cluster-name=%(cluster_name)s&filter=ig-name:eq:%(ig_name)s'
                        % {'cluster_name': cluster_name, 'ig_name': ig_name})
        t_init, _ = self.get_resource("initiators", params=params_value)
        #print(len(t_init.get('initiators')))
        if len(t_init.get('initiators')) == 0:
            err_msg = ("There are not initiators associated with %s initiator groups" % ig_name)
            return err_msg, False
        else:
            init_list = [x.get('name') for x in t_init.get('initiators')]
        for init_name in init_list:
            t, _ = self.get_initiator_info(init_name, cluster_name)
            init_wwpn = t.get('content').get('port-address')
            ig_os = t.get('content').get('operating-system')
            init_return_list.append({'initiator-name': init_name, 'port-address': init_wwpn, 'operating-system': ig_os})
        return_dict['initiators-info'] = init_return_list
        vol_creation, vol_creation_sts = self.create_multiple_volumes(volume_prefix_name, volume_suffix_count,
                                                                      num_of_volumes, volume_size, cluster_name)
        if vol_creation_sts is False:
            object_exist_status = True
        if object_exist_status is True:
            err_msg = "Error: initiator group or volume name already exists, please verify your inputs"
            return err_msg, False
        return_dict['ig-name'] = ig_name
        for vol in vol_creation:
            vol_msg, _ = self.create_lun_map(vol, ig_name, cluster_name)
        if cg_name:
            if self.does_a_object_exist(cg_name, "consistency-groups", cluster_name) is True:
                for vol in vol_creation:
                    _, _ = self.add_volume_to_consistency_group(cg_name, vol, cluster_name)
                return_dict['consistency-group-name'] = cg_name
            else:
                _, _ = self.create_consistency_group(cg_name, cluster_name, vol_creation)
                return_dict['consistency-group-name'] = cg_name
        vol_return_list = list()
        # time.sleep(12)
        # Following code is ensure that if vol_naa is "" then it will try to get naa till it is not "" or try to
        # 15 sec
        wait_count = 0
        wait_times = 30
        for vol in vol_creation:
            while wait_count < wait_times:
                t_vol, _ = self.get_volume_info(vol, cluster_name)
                vol_naa = t_vol.get('content').get('naa-name')
                if vol_naa != "":
                    wait_count = wait_times + 1
                wait_count += 1
                time.sleep(.5)
            v_size = t_vol.get('content').get('vol-size')
            vol_return_list.append({'vol-name': vol, 'vol-size': v_size, 'naa-name': vol_naa})
        return_dict['volumes-info'] = vol_return_list
        return return_dict, True

    def map_existing_volumes_to_new_fc_ig(self, ig_name, ig_os, wwpn_list, volume_list,  cluster_name, cg_name=None):
        """Create new volumes and initiator group and map them.

        :param ig_name: string - the name of initiator group (e.g. ServerName)
        :param ig_os: string - Operating System where initiator group resides (e.g. one of the following option
                      [solaris, aix, windows, esx, other, linux, hpux]
        :param wwpn_list: list - list of initiator's wwpn
        :param volume_list: string - list of existing volumes (e.g. ["vol1", "vol2"])
        :param cluster_name: string - the name of a cluster
        :param cg_name: string - the name of the consistency group
        :return: one of the following two:
                 string - some error msg, False
                 dict, True
                 Dict will be like following:
                 {'consistency-group-name': 'cg_esx01',
                    'ig-name': 'esx01',
                    'initiators-info': [{'initiator-name': 'esx01_HBA01',
                                      'operating-system': 'esx',
                                      'port-address': '200261000000001c'}],
                    'volumes-info': [{'naa-name': 'c0c5d38bfa22f054',
                                      'vol-name': 'ESXVol01',
                                      'vol-size': '1048576'}]
                 }
        """
        var_list = [ig_name, ig_os, wwpn_list, volume_list, cluster_name, cg_name]
        arg_list = [str, str, list, list, str, (type(None), str)]
        if self.verify_arguments_types(var_list,arg_list) is False:
            err_msg = "Error: one of more function input type is wrong. Please verify your input."
            return err_msg, False
        object_exist_status = False
        if self.does_a_object_exist(ig_name, "initiator-groups", cluster_name) is True:
            object_exist_status = True
        for init_wwpn in wwpn_list:
            init_wwn_sts, _ = self.search_initiator_by_wwn(init_wwpn, cluster_name)
            if init_wwn_sts is not None:
                object_exist_status = True
        init_count = 1
        for init_wwpn in wwpn_list:
            init_name = ("%s_HBA%.2d" % (ig_name, init_count))
            if self.does_a_object_exist(init_name, "initiators", cluster_name) is True:
                object_exist_status = True
            init_count += 1
        if ig_os not in ["solaris", "aix", "windows", "esx", "other", "linux", "hpux"]:
            err_msg = ("initiator os is %s. however, it only excepts [solaris, aix, windows, esx, other, linux, hpux] "
                       "values" % ig_os)
            return err_msg, False
        vol_list, vol_list_sts = self.do_all_objects_exist(volume_list, "volumes", cluster_name)
        if vol_list_sts is False:
            err_msg = ("Error: There are no volumes in %s cluster or these volumes do not exists: %s" %
                       (cluster_name, vol_list))
            return err_msg, False
        if object_exist_status is True:
            err_msg = "Error: initiator group, wwpn or initiator name already exists, please verify your inputs"
            return err_msg, False
        return_dict = dict()
        _, _ = self.create_initiator_group(ig_name, cluster_name)
        return_dict['ig-name'] = ig_name
        init_return_list = list()
        init_count = 1
        for init_wwpn in wwpn_list:
            init_name = ("%s_HBA%.2d" % (ig_name, init_count))
            _, _ = self.create_initiator(init_name, init_wwpn, ig_os, ig_name, cluster_name)
            init_return_list.append({'initiator-name': init_name, 'port-address': init_wwpn, 'operating-system': ig_os})
            init_count += 1
        return_dict['initiators-info'] = init_return_list
        for vol in volume_list:
            vol_msg, _ = self.create_lun_map(vol, ig_name, cluster_name)
        if cg_name:
            if self.does_a_object_exist(cg_name, "consistency-groups", cluster_name) is True:
                for vol in volume_list:
                    _, _ = self.add_volume_to_consistency_group(cg_name, vol, cluster_name)
                return_dict['consistency-group-name'] = cg_name
            else:
                _, _ = self.create_consistency_group(cg_name, cluster_name, volume_list)
                return_dict['consistency-group-name'] = cg_name
        vol_return_list = list()
        # time.sleep(12)
        # Following code is ensure that if vol_naa is "" then it will try to get naa till it is not "" or try to
        # 15 sec
        wait_count = 0
        wait_times = 30
        for vol in volume_list:
            while wait_count < wait_times:
                t_vol, _ = self.get_volume_info(vol, cluster_name)
                vol_naa = t_vol.get('content').get('naa-name')
                if vol_naa != "":
                    wait_count = wait_times + 1
                wait_count += 1
                time.sleep(.5)
            v_size = t_vol.get('content').get('vol-size')
            vol_return_list.append({'vol-name': vol, 'vol-size': v_size, 'naa-name': vol_naa})
        return_dict['volumes-info'] = vol_return_list
        return return_dict, True

    def map_existing_volumes_to_existing_fc_ig(self, ig_name, volume_list, cluster_name, cg_name=None):
        """Create new volumes and initiator group and map them.

        :param ig_name: string - the name of initiator group (e.g. ServerName)
        :param volume_list: list - list of volume name (e.g. ["Vol1", "Vol2"])
        :param cluster_name: string - the name of a cluster
        :param cg_name: string - the name of a consistency group
        :return: one of the following two:
                 string - some error msg, False
                 dict, True
                 Dict will be like following:
                 {'consistency-group-name': 'cg_esx01',
                    'ig-name': 'esx01',
                    'initiators-info': [{'initiator-name': 'esx01_HBA01',
                                      'operating-system': 'esx',
                                      'port-address': '200261000000001c'}],
                    'volumes-info': [{'naa-name': 'c0c5d38bfa22f054',
                                      'vol-name': 'ESXVol01',
                                      'vol-size': '1048576'}]
                 }
        """
        var_list = [ig_name, volume_list, cluster_name, cg_name]
        arg_list = [str, list, str, (type(None), str)]
        if self.verify_arguments_types(var_list, arg_list) is False:
            err_msg = "Error: one of more function input type is wrong. Please verify your input."
            return err_msg, False
        object_exist_status = False
        return_dict = dict()
        if self.does_a_object_exist(ig_name, "initiator-groups", cluster_name) is not True:
            err_msg = ("Error: initiator group name %s does not exist in %s cluster." % (ig_name, cluster_name))
            return err_msg, False
        init_return_list = list()
        params_value = ('cluster-name=%(cluster_name)s&filter=ig-name:eq:%(ig_name)s'
                        % {'cluster_name': cluster_name, 'ig_name': ig_name})
        t_init, _ = self.get_resource("initiators", params=params_value)
        #print(len(t_init.get('initiators')))
        if len(t_init.get('initiators')) == 0:
            err_msg = ("There are not initiators associated with %s initiator groups" % ig_name)
            return err_msg, False
        else:
            init_list = [x.get('name') for x in t_init.get('initiators')]
        for init_name in init_list:
            t, _ = self.get_initiator_info(init_name, cluster_name)
            init_wwpn = t.get('content').get('port-address')
            ig_os = t.get('content').get('operating-system')
            init_return_list.append({'initiator-name': init_name, 'port-address': init_wwpn, 'operating-system': ig_os})
        return_dict['initiators-info'] = init_return_list
        vol_list, vol_list_sts = self.do_all_objects_exist(volume_list, "volumes", cluster_name)
        if vol_list_sts is False:
            err_msg = ("Error: There are no volumes in %s cluster or these volumes do not exists: %s" %
                       (cluster_name, vol_list))
            return err_msg, False
        for vol in volume_list:
            _, t_sts = self.is_this_volume_map_to_this_ig(vol, ig_name, cluster_name)
            if t_sts is False:
                vol_msg, _ = self.create_lun_map(vol, ig_name, cluster_name)
        if cg_name:
            if self.does_a_object_exist(cg_name, "consistency-groups", cluster_name) is True:
                for vol in volume_list:
                    _, _ = self.add_volume_to_consistency_group(cg_name, vol, cluster_name)
                return_dict['consistency-group-name'] = cg_name
            else:
                _, _ = self.create_consistency_group(cg_name, cluster_name, volume_list)
                return_dict['consistency-group-name'] = cg_name
        vol_return_list = list()
        #time.sleep(12)
        # Following code is ensure that if vol_naa is "" then it will try to get naa till it is not "" or try to
        # 15 sec
        wait_count = 0
        wait_times = 30
        for vol in volume_list:
            while wait_count < wait_times:
                t_vol, _ = self.get_volume_info(vol, cluster_name)
                vol_naa = t_vol.get('content').get('naa-name')
                if vol_naa != "":
                    wait_count = wait_times + 1
                wait_count += 1
                time.sleep(.5)
            v_size = t_vol.get('content').get('vol-size')
            vol_return_list.append({'vol-name': vol, 'vol-size': v_size, 'naa-name': vol_naa})
        return_dict['volumes-info'] = vol_return_list
        return return_dict, True





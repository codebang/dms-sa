# coding: utf-8

"""
Copyright 2016 SmartBear Software

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Ref: https://github.com/swagger-api/swagger-codegen
"""

from pprint import pformat
from six import iteritems
import json


class HostSO(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        HostSO - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'mac': 'str',
            'ip': 'str',
            'host_name': 'str',
            'domain': 'str',
            'type': 'str'
        }

        self.attribute_map = {
            'mac': 'mac',
            'ip': 'ip',
            'host_name': 'hostName',
            'domain': 'domain',
            'type': 'type'
        }

        self._mac = None
        self._ip = None
        self._host_name = None
        self._domain = None
        self._type = None

    @property
    def mac(self):
        """
        Gets the mac of this HostSO.


        :return: The mac of this HostSO.
        :rtype: str
        """
        return self._mac

    @mac.setter
    def mac(self, mac):
        """
        Sets the mac of this HostSO.


        :param mac: The mac of this HostSO.
        :type: str
        """
        self._mac = mac

    @property
    def ip(self):
        """
        Gets the ip of this HostSO.


        :return: The ip of this HostSO.
        :rtype: str
        """
        return self._ip

    @ip.setter
    def ip(self, ip):
        """
        Sets the ip of this HostSO.


        :param ip: The ip of this HostSO.
        :type: str
        """
        self._ip = ip

    @property
    def host_name(self):
        """
        Gets the host_name of this HostSO.


        :return: The host_name of this HostSO.
        :rtype: str
        """
        return self._host_name

    @host_name.setter
    def host_name(self, host_name):
        """
        Sets the host_name of this HostSO.


        :param host_name: The host_name of this HostSO.
        :type: str
        """
        self._host_name = host_name

    @property
    def domain(self):
        """
        Gets the domain of this HostSO.


        :return: The domain of this HostSO.
        :rtype: str
        """
        return self._domain

    @domain.setter
    def domain(self, domain):
        """
        Sets the domain of this HostSO.


        :param domain: The domain of this HostSO.
        :type: str
        """
        self._domain = domain

    @property
    def type(self):
        """
        Gets the domain of this HostSO.


        :return: The domain of this HostSO.
        :rtype: str
        """
        return self._domain

    @type.setter
    def type(self, type):
        """
        Sets the domain of this HostSO.


        :param domain: The domain of this HostSO.
        :type: str
        """
        self._type = type

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other): 
        """
        Returns true if both objects are equal
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """ 
        Returns true if both objects are not equal
        """
        return not self == other

    def to_kafka_group_host(self, group):
        result = dict(mac=self._mac, ip=self._ip, groupId=group.id,
                      groupName=group.groupname, domain=self._domain, type=self._type)
        return result

    def to_kafka_user_host(self, user):
        result = dict(mac=self._mac, ip=self._ip, userID=user.id,
                      user_name=user.name, type=self._type)
        return json.dumps(result)

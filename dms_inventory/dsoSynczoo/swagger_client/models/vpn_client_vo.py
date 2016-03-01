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


class VPNClientVO(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        VPNClientVO - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'user_name': 'str',
            'ip': 'str',
            'group': 'str'
        }

        self.attribute_map = {
            'user_name': 'userName',
            'ip': 'ip',
            'group': 'group'
        }

        self._user_name = None
        self._ip = None
        self._group = None

    @property
    def user_name(self):
        """
        Gets the user_name of this VPNClientVO.


        :return: The user_name of this VPNClientVO.
        :rtype: str
        """
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        """
        Sets the user_name of this VPNClientVO.


        :param user_name: The user_name of this VPNClientVO.
        :type: str
        """
        self._user_name = user_name

    @property
    def ip(self):
        """
        Gets the ip of this VPNClientVO.


        :return: The ip of this VPNClientVO.
        :rtype: str
        """
        return self._ip

    @ip.setter
    def ip(self, ip):
        """
        Sets the ip of this VPNClientVO.


        :param ip: The ip of this VPNClientVO.
        :type: str
        """
        self._ip = ip

    @property
    def group(self):
        """
        Gets the group of this VPNClientVO.


        :return: The group of this VPNClientVO.
        :rtype: str
        """
        return self._group

    @group.setter
    def group(self, group):
        """
        Sets the group of this VPNClientVO.


        :param group: The group of this VPNClientVO.
        :type: str
        """
        self._group = group

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

    def to_kafka(self):
        result = dict(userName=self._user_name, ip=self._ip,
                      groupName=self._group)
        return result

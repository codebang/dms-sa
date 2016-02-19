import json
from connects import ConnectFactory

class ObjectFactory(type):
    meta_data = {}
    def __init__(cls,classname,bases,dict_):
        type.__init__(cls,classname,bases,dict_)
        if 'register' not in cls.__dict__:
            cls.meta_data[classname.lower()] = cls

    @classmethod
    def fromjson(cls,json_str):
        map = json.loads(json_str)
        return cls.meta_data[map["module"]](map)


class_dict = dict(register=True)

class ModelBase(object):
    def __init__(self,map):
        self.accountId = map["accountId"]
        self.operation = map["operation"]
        self.data = map["data"]
        self.fromMap(self.data)

    def fromMap(self,data):
        pass

    def execute(self):
        pass

Model = ObjectFactory("Model",(ModelBase,),class_dict)


class UserGroup(Model):
    def __init__(self,map):
        super(UserGroup, self).__init__(map)

    def fromMap(self,data):
        self.groupname = data["groupname"]
        self.id = data["id"]

    def execute(self):
        pass



if __name__ == '__main__':
    json_str = """
        {"accountId":"6bcd0ebf-a099-48aa-954c-38fa2732cade","module":"usergroup","operation":"create","result":"success","data":{"groupname":"eng","id":"cee2c7bf-24bf-4b45-8fe3-5c5854964f0e","accountUUID":"6bcd0ebf-a099-48aa-954c-38fa2732cade"}}
        """
    print ObjectFactory.fromjson(json_str)
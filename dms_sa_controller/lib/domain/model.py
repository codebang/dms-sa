from lib.utils import singleton

class ModelManager(object):
    def __init__(self):
        self.initmodel()


    def initmodel(self):
        self.model_base = {}
        self.model_base["basic"] = [Firewall(),VRouter(),DNS()]
        self.model_base["basic/ipsecvpn"] = [Firewall(),VRouter(),DNS(),IpsecVPN()]
        self.model_base["basic/ipsecvpn/vpc"] = [Firewall(),VRouter(),DNS(),IpsecVPN(),VPC()]


    def listsvcbypath(self,path):
        return self.model_base.get(path,None)

    def getsvfdefbyname(self,name):
        return ServiceBase.getServiceModel(name)


class ServiceBase(object):
    share_state = {}
    def __init__(self):
        self.type = self.__class__.__name__.lower()
        self.share_state[self.type] = self
        self.initprop()
        self.manage_neighbors = []
        self.service_neighbors = []

    @classmethod
    def getServiceModel(cls,name):
        return cls.share_state.get(name,None)



@singleton
class Firewall(ServiceBase):
    def initprop(self):
        self.os = "ubuntu"
        self.instancecount = 1



@singleton
class VRouter(ServiceBase):
    def initprop(self):
        self.os = "fedora"
        self.instancecount = 1
        self.service_neighbors = ["vpn"]
        self.manage_neighbors = ["vpn","dns"]

@singleton
class IpsecVPN(ServiceBase):
    def initprop(self):
        self.os = "centos"
        self.instancecount = 1
        self.service_neighbors=["vrouter"]
        self.manage_neighbors=["vrouter","dns"]

@singleton
class DNS(ServiceBase):
    def initprop(self):
        self.os = "ubuntu"
        self.instancecount = 1
        self.manage_neighbors = ["vpn","vrouter"]

@singleton
class VPC(ServiceBase):
    def initprop(self):
        self.os = "ubuntu"
        self.instancecount = 0



if __name__ == '__main__':
   mm =  ModelManager()
   print mm.getsvfdefbyname("vpn")
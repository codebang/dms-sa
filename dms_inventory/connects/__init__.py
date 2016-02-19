def singleton(cls):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return _singleton


@singleton
class ConnectFactory(object):
    def getConnect(self,conn_type):
        pass
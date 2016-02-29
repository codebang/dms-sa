import redis
from util import singleton
from util import ConfigurationHelper

@singleton
class ConnectFactory(object):
    def getConnect(self,conn_type):
        if conn_type == "redis":
            config = ConfigurationHelper()
            host = config.get("redis","host")
            port = config.get("redis","port")
            rd = redis.Redis(host,port)
            return redis.Redis(host,port)

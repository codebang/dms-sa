# coding: utf-8
import time
from kazoo.client import KazooClient
import logging



class ZookClient(object):

    def __init__(self, api_client=None):
        logging.basicConfig()
        # Create a client and start it
        self.zk = KazooClient()
        self.zk.start()

    def create_accounts_path(self, name, **kwargs):
        path = "/dso/" + name
        self.zk.ensure_path(path)
        self.zk.set(path, b"id: 7b4235ca-00fb-4dca-ad3e-8b6e3662631a\ngroupname: hr\ndescription: 人力资源")


    def create_accountinfo_path(self, account_id, **kwargs):
        self.zk.ensure_path("/app/someservice")

    def create_path(self, path, **kwargs):
        self.zk.ensure_path(path)

    def get_data(self, path):
        return self.zk.get(path)

    def test_tran(self):
        self.zk.delete("/app22")
        self.zk.create("/app22", b"" + '{"12": "12"}')

        tran = self.zk.transaction()
        tran.delete("/app22")
        tran.create("/app22", b"" + '{"22": "22"}')
        tran.commit()
        print "commit"


    def stop(self):
        # In the end, stop it
        self.zk.stop()

if __name__ == "__main__":
    try:
        # while True:
        #     client = ZookClient()
        #     # client.create_accounts_path("/test/has//32/")
        #     val = client.get_data("/dso/Mapping/Ip2Vm")
        #     print val
        #     time.sleep(45)
        client = ZookClient()
        client.test_tran()
    except Exception as exp:
        print exp.message






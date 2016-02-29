# coding: utf-8
__author__ = 'huiyu'

import time
from swagger_client.apis import account_api
from swagger_client.apis import vpnclient_api
import traceback
import sync_redis


def full_sync():
    result = []
    try:
        dso_account_client = account_api.AccountApi()

        current_page = 1
        size = 10
        # get one page count 10 for once,
        rtn = dso_account_client.accounts_get(current_page, size)
        accounts = rtn.results.item
        pages = rtn.total

        while current_page <= pages:
            # get account info for pre account
            for account in accounts:
                result.extend(account_sync(account.id))
            current_page += 1
            rtn = dso_account_client.accounts_get(current_page, size)
            accounts = rtn.results.item
            pages = rtn.total

    except Exception as exp:
        print exp.message
        traceback.print_exc()
    return result


def account_sync(account_id):
    try:
        dso_account_client = account_api.AccountApi()
        dso_vpn_client = vpnclient_api.VpnclientApi()

        account_info = dso_account_client.accounts_account_id_get(account_id)

        # get 1000 for now, FIXME
        vpn_info = dso_vpn_client.vpn_account_id_get(account_id, 1, 1000)
        vpn_clients = vpn_info.results.item

        return sync_redis.sync_to_redis(account_info, vpn_clients)

    except Exception as exp:
        print exp.message
        traceback.print_exc()


if __name__ == "__main__":
    start = time.time()
    full_sync()
    used = time.time() - start
    print "full sync finish, use %d sec " % used
    time.sleep(60)

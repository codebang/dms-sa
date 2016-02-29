# from ..utils import logger
import json


def sync_to_redis(account_info, vpn_clients):

    result = []

    # logger.info("start sync dso info to redis, " + account_info.id)
    account_id = account_info.id

    # account
    result.append(gen_create_msg(
        account_id, "account", account_info.to_kafka()))

    # sync each group
    for group in account_info.groups:
        result.append(gen_create_msg(account_id, "usergroup", group.to_kafka()))
        for user in group.users:
            result.append(gen_create_msg(account_id, "user", user.to_kafka(group)))
            for host in user.hosts:
                result.append(gen_create_msg(account_id, "host", host.to_kafka_user_host(user)))

        for server in group.servers:
            result.append(gen_create_msg(account_id, "host", server.to_kafka_group_host(group)))

    # sync vpn
    for vpn in vpn_clients:
        result.append(gen_create_msg(account_id, "vpn", vpn.to_kafka()))

    return result


def inventory_json(account_id, module, operation, result, data):
        message = {
            "accountId": account_id,
            "module": module,
            "operation": operation,
            "result": result,
            "data": data
        }
        return json.dumps(message)


def gen_create_msg(account_id, module, data):
    return inventory_json(account_id, module, "create", "success", data)
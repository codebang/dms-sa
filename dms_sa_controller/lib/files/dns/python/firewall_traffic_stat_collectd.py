# 1. 'sudo iptaccount -a' to get all tables like internet, intragrp, intergrp
# 2. use 'iptaccount -l internet' to get users details for accessing internet
# 3. use 'iptaccount -l intergrp' to get user group details for accessing internet
# 4. use 'sudo policy.sh show' to get sent bytes and dropped
import subprocess
import socket
import traceback


class CmdError(Exception):
    pass


def run_policy_cmd():
    cmd = "sudo policy.sh show"
    lines = run(cmd)
    output = []
    index = None
    for idx, line in enumerate(lines):
        if 'qdiscs statistics' in line:
            index = idx
            break
    index += 1
    lines = lines[index:]
    for line in lines:
        if 'qdisc' in line or 'Sent' in line:
            output.append(line)
    # ['qdisc htb 1: xxxx', 'Sent xxx', 'qdisc pfifo: xxx', 'Sent xxx']

    result = {}
    key = output[0]
    for item in output:
        if 'qdisc' in item:
            key = item
            continue
        if 'Sent' in item:
            value = item
            result[key] = value
            continue
    # {'qdisc htb 1:xxx': 'Sent xxx', 'qdisc pfifo: xxx': 'Sent xxx'}
    return result


def get_policy_stat():
    output = run_policy_cmd()
    stat_dict = {}
    for key, value in output.iteritems():
        policy_name = parse_policy_name(key)
        policy_value = parse_policy_stats(value)
        stat_dict[policy_name] = policy_value
    # {'qdisc_htb_1':[dropped, sent_bytes, sent_pkt], 'qdisc_pfifo_1100':[dropped, sent_bytes, sent_pkt]}
    return stat_dict


def parse_policy_name(line):
    return line.split(':')[0].strip().replace(' ','_')


def parse_policy_stats(line):
    dropped = line.split('dropped')[1].split(',')[0].strip()
    sent_bytes = line.split('bytes')[0].strip().replace('Sent','').strip()
    sent_pkt = line.split('pkt')[0].strip().split('bytes')[1].strip()
    return [dropped, sent_bytes, sent_pkt]


def get_internet_stat():
    output = run_internet_cmd()
    internet_stat = get_traffic_stat(output)
    # {"10.1.4.77":[src_bytes, src_packets, dst_bytes, src_packets, dst_packets], }
    return internet_stat


def get_intergrp_stat():
    output = run_intergrp_cmd()
    intergrp_stat = get_traffic_stat(output)
    # {"10.1.4.77":[src_bytes, src_packets, dst_bytes, dst_packets], }
    return intergrp_stat


def get_intragrp_stat():
    output = run_intragrp_cmd()
    intragrp_stat = get_traffic_stat(output)
    # {"10.1.4.77":[src_bytes, src_packets, dst_bytes, dst_packets], }
    return intragrp_stat


def get_traffic_stat(cmd_result):
    traffic_stat = {}
    for line in cmd_result:
        ip = parse_ip_info(line)
        src_bytes = parse_src_bytes(line)
        src_packets = parse_src_packets(line)
        dst_bytes = parse_dst_bytes(line)
        dst_packets = parse_dst_packets(line)
        traffic_stat[ip] = [src_bytes, src_packets, dst_bytes, dst_packets]
    # {"10.1.4.77":[src_bytes, src_packets, dst_bytes, dst_packets], }
    return traffic_stat


def run_intergrp_cmd():
    cmd = 'sudo iptaccount -l intergrp | grep ^IP'
    result = run_traffic_cmd(cmd)
    return result


def run_internet_cmd():
    cmd = 'sudo iptaccount -l internet | grep ^IP'
    result = run_traffic_cmd(cmd)
    return result


def run_intragrp_cmd():
    cmd = 'sudo iptaccount -l intragrp | grep ^IP'
    result = run_traffic_cmd(cmd)
    return result


def parse_ip_info(line):
    return line.split("SRC")[0].split(":")[1].strip()


def parse_src_bytes(line):
    return line.split('bytes:')[1].split('DST')[0].strip()


def parse_src_packets(line):
    return line.split('packets:')[1].split('bytes')[0].strip()


def parse_dst_bytes(line):
    return line.split('bytes:')[-1].strip()


def parse_dst_packets(line):
    return line.split('DST packets:')[1].split('bytes')[0].strip()


def run_traffic_cmd(cmd):
    lines = run(cmd)
    result = []
    for line in lines:
        if 'packets' in line and 'bytes' in line:
            result.append(line)
    return result


def run(cmd):
    try:
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True)
        (stdout, stderr) = proc.communicate()
        return stdout.split("\n")
    except Exception as err:
        raise CmdError("failed to execute command: %s, reason: %s" % (' '.join(cmd), err.message))


def get_host_name():
    return socket.gethostname().replace("-","_")


def get_delta_value(org_dict, latest_dict):
        # {"10.1.4.77":[src_bytes, src_packets, dst_bytes, dst_packets], }
        delta_dict = {}
        for key, values in latest_dict.iteritems():
            if org_dict.has_key(key):
                org_value = org_dict.get(key)
                src_bytes = int(values[0]) - int(org_value[0])
                src_packets = int(values[1]) - int(org_value[1])
                dst_bytes = int(values[2]) - int(org_value[2])
                dst_packets = int(values[3]) - int(org_value[3])
                delta_dict[key] = [src_bytes, src_packets, dst_bytes, dst_packets]
                org_dict[key] = values
            else:
                delta_dict[key] = values
                org_dict[key] = values

        for key in org_dict.keys():
            if latest_dict.has_key(key) is False:
                org_dict.pop(key)
        return delta_dict


def get_policy_delta_value(org_dict, latest_dict):
        # {'qdisc_htb_1':[dropped, sent_bytes, sent_pkt], 'qdisc_pfifo_1100':[dropped, sent_bytes, sent_pkt]}
        delta_dict = {}
        for key, values in latest_dict.iteritems():
            if org_dict.has_key(key):
                org_value = org_dict.get(key)
                dropped = int(values[0]) - int(org_value[0])
                sent_bytes = int(values[1]) - int(org_value[1])
                sent_pkt = int(values[2]) - int(org_value[2])
                delta_dict[key] = [dropped, sent_bytes, sent_pkt]
                org_dict[key] = values
            else:
                delta_dict[key] = values
                org_dict[key] = values
        return delta_dict


class FireWallUserStatMon(object):
    def __init__(self):
        self.plugin_name = "firewall_traffic_stat"
        self.interval = 5
        self.hostname = get_host_name()
        self.interfaces = ""
        self.verbose_logging = False
        self.account_id = None
        self.vm_type = None

    def log_verbose(self, msg):
        if not self.verbose_logging:
            return
        collectd.info('%s plugin [verbose]: %s' % (self.plugin_name, msg))

    def init(self):
        self.INTERNET_STAT = get_internet_stat()
        self.INTERGRP_STAT = get_intergrp_stat()
        self.INTRAGRP_STAT = get_intragrp_stat()
        self.POLICY_BASE_LINE = get_policy_stat()

    def configure_callback(self, conf):
        for node in conf.children:
            val = str(node.values[0])

            if node.key == 'HostName':
                self.hostname = val
            elif node.key == 'Interval':
                self.interval = int(float(val))
            elif node.key == 'Verbose':
                self.verbose_logging = val in ['True', 'true']
            elif node.key == 'PluginName':
                self.plugin_name = val
            elif node.key == "AccountId":
                self.account_id = val
            elif node.key == "VmType":
                self.vm_type = val
            else:
                collectd.warning('[plugin] %s: unknown config key: %s' % (self.plugin_name, node.key))

    def dispatch_value(self, plugin, host, type, type_instance, plugin_instance, value):
        self.log_verbose("Dispatching value plugin=%s, host=%s, type=%s, type_instance=%s, plugin_instance=%s, value=%s" %
                         (plugin, host, type, type_instance, plugin_instance, value))
        val = collectd.Values(type=type)
        val.plugin = plugin
        val.host = host
        val.type_instance = type_instance
        val.plugin_instance = plugin_instance
        val.interval = self.interval
        val.values = [value]
        val.dispatch()
        self.log_verbose("Dispatched value plugin=%s, host=%s, type=%s, type_instance=%s, plugin_instance=%s, value=%s" %
                         (plugin, host, type, type_instance, plugin_instance, value))

    def read_callback(self):
        try:
            internet_latest_stat = get_internet_stat()
            intergrp_latest_stat = get_intergrp_stat()
            intragrp_latest_stat = get_intragrp_stat()
            policy_latest_stat = get_policy_stat()

            internet_delta_stat = get_delta_value(self.INTERNET_STAT, internet_latest_stat)
            intergrp_delta_stat = get_delta_value(self.INTERGRP_STAT, intergrp_latest_stat)
            intragrp_latest_stat = get_delta_value(self.INTRAGRP_STAT, intragrp_latest_stat)
            policy_delta_stat = get_policy_delta_value(self.POLICY_BASE_LINE, policy_latest_stat)
            host = "%s__%s__%s" % (self.account_id, self.hostname, self.vm_type)
            # {"10.1.4.77":[src_bytes, src_packets, dst_bytes, dst_packets], }
            for ip, value in internet_delta_stat.iteritems():
                type_instance = ip
                plugin_instance = 'internet'
                self.dispatch_value(self.plugin_name, host, "src_bytes", type_instance, plugin_instance, value[0])
                self.dispatch_value(self.plugin_name, host, "src_packets", type_instance, plugin_instance, value[1])
                self.dispatch_value(self.plugin_name, host, "dst_bytes", type_instance, plugin_instance, value[2])
                self.dispatch_value(self.plugin_name, host, "dst_packets", type_instance, plugin_instance, value[3])
            for ip, value in intergrp_delta_stat.iteritems():
                type_instance = ip
                plugin_instance = 'intergrp'
                self.dispatch_value(self.plugin_name, host, "src_bytes", type_instance, plugin_instance, value[0])
                self.dispatch_value(self.plugin_name, host, "src_packets", type_instance, plugin_instance, value[1])
                self.dispatch_value(self.plugin_name, host, "dst_bytes", type_instance, plugin_instance, value[2])
                self.dispatch_value(self.plugin_name, host, "dst_packets", type_instance, plugin_instance, value[3])
            for ip, value in intragrp_latest_stat.iteritems():
                type_instance = ip
                plugin_instance = 'intragrp'
                self.dispatch_value(self.plugin_name, host, "src_bytes", type_instance, plugin_instance, value[0])
                self.dispatch_value(self.plugin_name, host, "src_packets", type_instance, plugin_instance, value[1])
                self.dispatch_value(self.plugin_name, host, "dst_bytes", type_instance, plugin_instance, value[2])
                self.dispatch_value(self.plugin_name, host, "dst_packets", type_instance, plugin_instance, value[3])
            for policy_name, value in policy_delta_stat.iteritems():
                type_instance = policy_name
                plugin_instance = 'policy.sh'
                self.dispatch_value(self.plugin_name, host, "dropped", type_instance, plugin_instance, value[0])
                self.dispatch_value(self.plugin_name, host, "sent_bytes", type_instance, plugin_instance, value[1])
                self.dispatch_value(self.plugin_name, host, "sent_pkt", type_instance, plugin_instance, value[2])
        except Exception as exp:
            self.log_verbose(traceback.print_exc())
            self.log_verbose("plugin %s run into exception" % (self.plugin_name))
            self.log_verbose(exp.message)


if __name__ == '__main__':
    print "************\n"
    # print str(get_intergrp_stat())
    # print "***********\n"
    # print str(get_internet_stat())
    # print "************\n"
    # print str(get_intragrp_stat())
    # print "**********\n"
    # print str(get_policy_stat())
    # print '------------------\n'
    a = get_internet_stat()
    print a
    import time
    time.sleep(10)
    print '------------------\n'
    b = get_internet_stat()
    c = get_delta_value(a, b)
    print '---delta value----'
    print c

    print "*********policy*****"
    a = get_policy_stat()
    print a
    import time
    time.sleep(10)
    print '------------------\n'
    b = get_policy_stat()
    c = get_policy_delta_value(a, b)
    print '---delta value----'
    print c
else:
    import collectd
    firewall_status = FireWallUserStatMon()
    collectd.register_config(firewall_status.configure_callback)
    collectd.register_init(firewall_status.init)
    collectd.register_read(firewall_status.read_callback)
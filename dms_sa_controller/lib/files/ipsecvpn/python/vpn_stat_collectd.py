#!/usr/bin/env python
#coding=utf-8

import socket
import subprocess
import traceback


class CmdError(Exception):
    pass


class VPNMetric(object):
    def __init__(self):
        self.init_dict = self.convert_metrics()

    def get_all_statistics(self):
        '''
        cmd to generate rx,tx info, no user info in rx
        '''
        org_result = self._run("sudo /usr/local/sbin/ipsec spi | grep -v ^esp")
        result = []
        for line in org_result:
            if '@' in line:
                result.append(line)
        return result

    def get_all_user_info(self):
        '''
        cmd to generate user info,
        '''
        org_result = self._run("sudo /usr/local/sbin/ipsec auto --status | grep tun")
        result = []
        for line in org_result:
            if '@' in line:
                result.append(line)
        return result

    def _run(self, cmd):
        try:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True)
            (stdout, stderr) = proc.communicate()
            output = stdout.split('\n')
            print("cmd %s output is %s" % (cmd, output))
            return output
        except Exception as err:
            raise CmdError("failed to execute command: %s, reason: %s" % (' '.join(cmd), err.message))

    def parse_each_statistic(self, line):
        if 'dir=out' in line:
            src_key = pick_field(line, '@', '0x', 0, 1)
            packets = pick_field(line, 'packets(', ',')
            bytes = pick_field(line, 'bytes(', ',')
            key = 'out_%s' % (src_key)
            value = [packets, bytes]
            '''[out_100f, [packets, bytes]]'''
            return [key, value]
        if 'dir=in' in line:
            src_key = pick_field(line, '@', '0x', 0, 1)
            packets = pick_field(line, 'packets(', ',')
            bytes = pick_field(line, 'bytes(', ',')
            user_ip = pick_field(line, 'policy=', '/')
            key = 'in_%s' % (src_key)
            value = [packets, bytes, user_ip]
            return [key, value]

    def parse_each_user(self, user_info_line):
        info_lst = user_info_line.split(' ')
        '''[tun.100f@64.104.163.11, tun.1010@192.168.9.100]
           [out_100f, in_1010]
        '''
        return ['out_%s' % self.get_tun_index(info_lst[-4]), 'in_%s' % self.get_tun_index(info_lst[-3])]

    def get_tun_index(self, tun_line):
        '''convert tun.100f@x.x.x.x to 100f'''
        return tun_line.split('@')[0].replace("tun.","")

    def _parse_all_user_info(self):
        output = self.get_all_user_info()
        users_dict= {}
        for element in output:
            user_info = self.parse_each_user(element)
            users_dict[user_info[0]] = user_info[1]
        '''{"out_100f":"in_1010", }'''
        return users_dict

    def _parse_all_statistics(self):
        org_result = self.get_all_statistics()
        stat_dict = {}
        for line in org_result:
            stat = self.parse_each_statistic(line)
            stat_dict[stat[0]] = stat[1]
        '''{"out_100f":[packets, bytes], "in_1010":[packets, bytes, user_ip], }'''
        return stat_dict

    def parse_all_user_info(self, users):
        output = users
        users_dict= {}
        for element in output:
            user_info = self.parse_each_user(element)
            users_dict[user_info[0]] = user_info[1]
        '''{"out_100f":"in_1010", }'''
        return users_dict

    def parse_all_statistics(self, stats):
        org_result = stats
        stat_dict = {}
        for line in org_result:
            stat = self.parse_each_statistic(line)
            stat_dict[stat[0]] = stat[1]
        '''{"out_100f":[packets, bytes], "in_1010":[packets, bytes, user_ip], }'''
        return stat_dict

    def find_user_ip(self, out_key, user_dict, stat_dict):
        in_key = user_dict.get(out_key)
        stat_info = stat_dict.get(in_key)
        return stat_info[2]

    def compose_metrics(self):
        stat_dict = self._parse_all_statistics()
        user_dict = self._parse_all_user_info()
        metrics_dict = {}
        for key, value in stat_dict.iteritems():
            if 'in' in key:
                metrics_dict[key] = value
            if 'out' in key:
                #out_1005,
                user_ip = self.find_user_ip(key, user_dict, stat_dict)
                value.append(user_ip)
                metrics_dict[key] = value
        '''{"out_100f":[packets, bytes, user_ip], "in_1010":[packets, bytes, user_ip], }'''
        return metrics_dict

    def convert_metrics(self):
        '''use in/out and user_ip as the key'''
        org_metrics = self.compose_metrics()
        final_metrics = {}

        for key, value in org_metrics.iteritems():
            new_key=""
            if 'out' in key:
                new_key = 'out__%s' % value[2]
            if 'in' in key:
                new_key = 'in__%s' % value[2]
            value = value[:2]
            final_metrics[new_key] = value
        '''{"out__10.x.x.x":[packets, bytes], "in__10.x.x.x":[packets, bytes], }'''
        return final_metrics

    def test_convert_metrics(self, dict):
        final_metrics = {}

        for key, value in dict.iteritems():
            new_key=""
            if 'out' in key:
                new_key = 'out__%s' % value[2]
            if 'in' in key:
                new_key = 'in__%s' % value[2]
            value = value[:2]
            final_metrics[new_key] = value
        '''{"out__10.x.x.x":[packets, bytes], "in__10.x.x.x":[packets, bytes], }'''
        return final_metrics

    def purge_not_existing_user(self, latest_metric):
        for key in self.init_dict.keys():
            if latest_metric.has_key(key):
                pass
            else:
                self.init_dict.pop(key, None)

    def get_delta_metrics(self):
        latest_metric = self.convert_metrics()
        "delete not existing user firstly from org metric"
        self.purge_not_existing_user(latest_metric)
        delta_metric = {}
        for key, value in latest_metric.iteritems():
            if self.init_dict.has_key(key):
                org_value = self.init_dict.get(key)
                delta_value = [float(value[0])-float(org_value[0]), float(value[1])-float(org_value[1])]
                self.init_dict[key] = value
                delta_metric[key] = delta_value
            else:
                delta_value = [float(value[0]), float(value[1])]
                self.init_dict[key] = delta_value
                delta_metric[key] = delta_value
        '''{"out__10.x.x.x":[packets, bytes], "in__10.x.x.x":[packets, bytes], }'''
        return delta_metric

    def test_compose_metrics(self, stat_lst, user_lst):
        stat_dict = self.parse_all_statistics(stat_lst)
        user_dict = self.parse_all_user_info(user_lst)
        metrics_dict = {}
        for key, value in stat_dict.iteritems():
            if 'in' in key:
                metrics_dict[key] = value
            if 'out' in key:
                user_ip = self.find_user_ip(key, user_dict, stat_dict)
                value.append(user_ip)
                metrics_dict[key] = value
        '''{"out_100f":[packets, bytes, user_ip], "in_1010":[packets, bytes, user_ip], }'''
        return metrics_dict


def pick_field(org_str, first_separator, second_separator, first_index=1, second_index=0):
    field = org_str.split(first_separator)[first_index].split(second_separator)[second_index]
    return field


def get_host_name():
        return socket.gethostname().replace("-","_")


class VPNMetricMon(object):
    def __init__(self):
        self.plugin_name = "vpn_stat"
        self.interval = 5
        self.hostname = ""
        self.account_name = None
        self.account_id = None
        self.vm_type = None
        self.verbose_logging = False

    def log_verbose(self, msg):
        if not self.verbose_logging:
            return
        collectd.info('%s plugin [verbose]: %s' % (self.plugin_name, msg))

    def configure_callback(self, conf):
        for node in conf.children:
            val = str(node.values[0])
            if node.key == 'HostName':
                self.hostname = val
            elif node.key == 'Interval':
                self.interval = int(float(val))
            elif node.key == 'Verbose':
                self.verbose_logging = val in ['True', 'true']
            elif node.key == "AccountId":
                self.account_id = val
            elif node.key == "VmType":
                self.vm_type = val
            elif node.key == "PluginName":
                self.plugin_name = val
            else:
                collectd.warning('[plugin] %s: unknown config key: %s' % (self.plugin_name, node.key))

    def dispatch_value(self, plugin, host, type, type_instance, value):
        self.log_verbose("Dispatching value plugin=%s, host=%s, type=%s, type_instance=%s, value=%s" %
                         (plugin, host, type, type_instance, str(value)))
        val = collectd.Values(type=type)
        val.plugin = plugin
        val.host = host
        val.type_instance = type_instance
        val.values = [value]
        val.dispatch()
        self.log_verbose("Dispatched value plugin=%s, host=%s, type=%s, type_instance=%s, value=%s" %
                         (plugin, host, type, type_instance, str(value)))

    def read_callback(self):
        try:
            self.log_verbose("plugin %s read callback called" % self.plugin_name)
            vpn_metric = VPNMetric()
            statuses = vpn_metric.compose_metrics()
            '''{"out__user_ip":[packets, bytes], "in__user_ip":[packets, bytes], }'''
            for key, value in statuses.iteritems():
                '''type_instance=user_ip, plugin_instance=out/in, type=in_packets/in_bytes,
                host=account_name__host_name__vm_type, value=packets_value/bytes_value'''
                host = "%s__%s__%s" % (self.account_id, self.hostname, self.vm_type)
                if 'out' in key:
                    type_instance = key.split('_')[1]
                    self.dispatch_value(self.plugin_name, host, "out_packets", type_instance, value[0])
                    self.dispatch_value(self.plugin_name, host, "out_bytes", type_instance, value[1])
                if 'in' in key:
                    type_instance = key.split('_')[1]
                    self.dispatch_value(self.plugin_name, host, "in_packets", type_instance, value[0])
                    self.dispatch_value(self.plugin_name, host, "in_bytes", type_instance, value[1])

        except Exception as exp:
            self.log_verbose(traceback.print_exc())
            self.log_verbose(exp.message)


if __name__ == '__main__':
    users = []
    with open("./user.txt", 'r') as f:
        for line in f:
            users.append(line)

    stats = []
    with open("./stats.txt", 'r') as f:
        for line in f:
            stats.append(line)

    vpn_status = VPNMetric()

    result = vpn_status.test_compose_metrics(stats,users)
    result = vpn_status.test_convert_metrics(result)
    print str(result)
else:
    import collectd
    vpn_mon = VPNMetricMon()
    collectd.register_config(vpn_mon.configure_callback)
    collectd.register_read(vpn_mon.read_callback)


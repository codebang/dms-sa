#!/usr/bin/env python
#coding=utf-8

import socket
import subprocess
import traceback


class CmdError(Exception):
    pass


class IfconfigStatus(object):
    def __init__(self, interfaces="eth0,eth1"):
        self.interfaces = interfaces.split(',')
        self.init_dict = {}
        for interface in self.interfaces:
            self.init_dict[interface] = self.get_interface_status(interface)

    def set_interface_value(self, interface, value):
        self.init_dict[interface] = value

    def get_interface_value(self, interface, value):
        return self.init_dict[interface]

    def get_interfaces_delta_value(self):
        delta_value_dict= {}
        for interface in self.interfaces:
            latest_result = self.get_interface_status(interface)
            old_result = self.init_dict[interface]
            delta_value_dict[interface] = [float(latest_result[0])-float(old_result[0]), float(latest_result[1])-float(old_result[1])]
            self.init_dict[interface] = latest_result
        return delta_value_dict

    def get_interface_status(self, interface):
        cmd = self._compose_command(interface)
        output = self._run(cmd)
        for line in output:
            if 'RX packets' in line and ':' not in line:
                rx_bytes = line.split('bytes')[1].split('(')[0].strip()
            if 'TX packets' in line and ':' not in line:
                tx_bytes = line.split('bytes')[1].split('(')[0].strip()
            if 'RX bytes:' in line:
                rx_bytes = line.split('RX bytes:')[1].split(' ')[0]
                tx_bytes = line.split('TX bytes:')[1].split(' ')[0]
        return [rx_bytes, tx_bytes]

    def _compose_command(self, interface):
        cmd = "sudo ifconfig %s" % interface
        return cmd

    def _run(self, cmd):
        try:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True)
            (stdout, stderr) = proc.communicate()
            output = stdout.split("\n")
            print("cmd %s output is %s" % (cmd, output))
            result = []
            for line in output:
                if 'RX bytes' in line or 'RX packets' in line or 'TX packets' in line:
                    result.append(line)
            if result is None:
                raise CmdError("failed to execute command %s, outputis %s" % (cmd, output))
            return result
        except Exception as err:
            raise CmdError("failed to execute command: %s, reason: %s" % (' '.join(cmd), err.message))


def get_host_name():
        return socket.gethostname().replace("-","_")


class IfconfigStatusMon(object):
    def __init__(self):
        self.plugin_name = "interface_stat"
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

    def configure_callback(self, conf):
        for node in conf.children:
            val = str(node.values[0])

            if node.key == 'Hostname':
                self.hostname = val
            elif node.key == 'Interval':
                self.interval = int(float(val))
            elif node.key == 'Verbose':
                self.verbose_logging = val in ['True', 'true']
            elif node.key == 'PluginName':
                self.plugin_name = val
            elif node.key == 'Interfaces':
                self.interfaces = val
            elif node.key == "AccountId":
                self.account_id = val
            elif node.key == "VmType":
                self.vm_type = val
            elif node.key == "HostName":
                self.hostname = val
            else:
                collectd.warning('[plugin] %s: unknown config key: %s' % (self.plugin_name, node.key))

    def dispatch_value(self, plugin, host, type, type_instance, value):
        self.log_verbose("Dispatching value plugin=%s, host=%s, type=%s, type_instance=%s, value=%s" %
                         (plugin, host, type, type_instance, str(value)))
        val = collectd.Values(type=type)
        val.plugin = plugin
        val.host = host
        val.type_instance = type_instance
        val.interval = self.interval
        val.values = [value]
        val.dispatch()
        self.log_verbose("Dispatched value plugin=%s, host=%s, type=%s, type_instance=%s, value=%s" %
                         (plugin, host, type, type_instance, str(value)))

    def read_callback(self):
        try:
            self.log_verbose("plugin %s read callback called, process is: %s" % (self.plugin_name, self.interfaces))
            interface_status = IfconfigStatus(self.interfaces)
            statuses = interface_status.get_interfaces_delta_value()
            host = "%s__%s__%s" % (self.account_id, self.hostname, self.vm_type)
            for interface, value in statuses.iteritems():
                type_instance = interface
                # self.dispatch_value(self.plugin_name, host, "if_stats", type_instance, value[0], str(value[1]))
                self.dispatch_value(self.plugin_name, host, "rx_bytes", type_instance, value[0])
                self.dispatch_value(self.plugin_name, host, "tx_bytes", type_instance, value[1])
        except Exception as exp:
            self.log_verbose(traceback.print_exc())
            self.log_verbose("plugin %s run into exception" % (self.plugin_name))
            self.log_verbose(exp.message)

    def _escape_proc_name(self, proc):
        if str(proc) == '0':
            return '0'
        return proc.replace('[', '').replace(']', '').replace('/', '.').replace("-", "_")


if __name__ == '__main__':
    # process_status = ProcessStatus("pyth[on], /usr/bin/ss[hd], ja[va]")
    ifconfig_status = IfconfigStatus("eth0,eth1")
    import time
    time.sleep(3)
    result = ifconfig_status.get_interfaces_delta_value()
    time.sleep(3)
    result = ifconfig_status.get_interfaces_delta_value()
    print str(result)
else:
    import collectd
    ifconfig_status = IfconfigStatusMon()
    collectd.register_config(ifconfig_status.configure_callback)
    collectd.register_read(ifconfig_status.read_callback)


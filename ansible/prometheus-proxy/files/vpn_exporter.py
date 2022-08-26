import re
import datetime
import logging

# This script is a simple exporter that collects metrics from vpn log files. This metrics are integrated into node exporter,
# so they can be accessed by prometheus.
class Metric:
    total_realm = 2
    total_active_client = 0
    def __init__(self):
        self.number_active_clients = 0
        self.remaining_ips = 254


class Realm:
    """
    This class defines the type of vpn connection that is being used by the client.
    """
    def __init__(self, name, logfile):
        """
        the init method takes in the name of the realm of type of vpn connection and a logfile which is where openvpn logs
        its status.

        :param name: the name of the realm
        :param logfile: the status file of the realm
        """
        self.name = name
        self.logfile = logfile
        self.metrics = []


    def parse_log(self):
        """
        the logfile or status file is parsed to obtain info about the vpn client.
        :returns metrics: This is a list of all the clients currently connected together with their info.
        """
        f = open(self.logfile, 'r')
        order = ["type", "common_name", "real_address", "virtual_address", "bytes_rec", "bytes_send",
                 "day", "month", "date", "time_t", "year", "connected_since", "username", "client_id", "peer_id"]
        for line in f.readlines():
            client = re.match("^CLIENT_LIST[\s\w\d\.:-]+", line)
            if client is not None:
                stats = line.split()
                stats = [x.strip() for x in stats]
                data_form = {key: value for key, value in zip(order, stats)}
                self.metrics.append(data_form)
        f.close()
        return self.metrics

    def compute_metrics(self, metric):
        """
        the metrics are calculated here.
        :param metric: a class that contains info about the number of clients per realm. The metrics are caculated
        and returned to be printed.
        """
        metric.number_active_clients = len(self.metrics)
        metric.remaining_ips -= metric.number_active_clients
        return metric

    def write_metrics(self, metric):
        """
        the metrics are written into stdout. Eventually this metrics would end up in a .prom, a textfile collector by
        prometheus.
        """
        print(f'vpn_active_clients{{realm="{self.name}"}} {metric.number_active_clients}')
        print(f'vpn_remaining_ips_per_realm{{realm="{self.name}"}} {metric.remaining_ips}')
        for client in self.metrics:
            try:
                date = datetime.datetime.fromtimestamp(int(client["connected_since"])).strftime("%Y-%m-%d_%H:%M:%S")
                print(f'vpn_client_info{{realm="{self.name}",client_name="{client["common_name"]}",connected_since="{date}"}} 1')
            except Exception as e:
                raise e



def compute_stats(realm_name, log_path):
    realm  = Realm(realm_name, log_path)
    realm.parse_log()
    _metric = Metric()
    _metric = realm.compute_metrics(_metric)
    realm.write_metrics(_metric)
    return _metric.number_active_clients

def main():
    total_clients  = 0
    openvpn_server_realms = [{"name":"internal-std", "status":"/var/log/openvpn/internal-std.status"},
                             {"name":"internal-all", "status":"/var/log/openvpn/internal-all-traffic.status"}]
    for _realm in openvpn_server_realms:
        total_clients+=compute_stats(_realm["name"], _realm["status"])
    print(f'vpn_total_active_clients {total_clients}')


if __name__ == "__main__":
    main()




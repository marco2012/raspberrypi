# -*- coding: utf-8 -*-
import scapy.all as scapy

GATEWAY = "192.168.1.1/24"
known_hosts_dict = {
    "MAC_ADDRESS" : "NAME"
}

def print_result(results_list):
    print("IP\t\t\tMAC Address")
    print("------------------------------------------------")
    for client in results_list:
        print(client["ip"] + "\t\t" + client["mac"])

# https://medium.com/@777rip777/simple-network-scanner-with-python-and-scapy-802645073190
def scan():
    ip                    = GATEWAY
    arp_request           = scapy.ARP(pdst=ip)
    broadcast             = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list         = scapy.srp(arp_request_broadcast, timeout=1,
                              verbose=False)[0]
    clients_list = []
    mac_address_list = []
    for element in answered_list:
        client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        clients_list.append(client_dict)
        mac_address_list.append(element[1].hwsrc)
    # print_result(clients_list)
    return mac_address_list


def check_who_is_home(mac_address_list):
    at_home = "Nessuno"
    for m in mac_address_list:
        x = known_hosts_dict.get(m)
        if x and not x in at_home:
            at_home = x + ", "
    
    p = at_home.split(',')
    if at_home == "Nessuno":
        print("Sembra che a casa non ci sia nessuno.")
    elif len(p) < 3:
        print( "A casa c'è {}.".format(p[0]) )
    else:
        print("A casa ci sono {}".format(at_home))


if __name__ == "__main__":
    scan_result = scan()
    check_who_is_home(scan_result)

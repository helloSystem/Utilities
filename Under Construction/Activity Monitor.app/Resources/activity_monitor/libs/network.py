import psutil


def get_available_network_interfaces():
    """
    Get only up and running network interfaces

    :return: interfaces up and running list
    :rtype: list
    """
    stats = psutil.net_if_stats()

    available_networks = []
    for interface, address_list in psutil.net_if_addrs().items():
        if any(getattr(addr, 'address').startswith("169.254") for addr in address_list):
            continue
        elif interface in stats and getattr(stats[interface], "isup"):
            available_networks.append(interface)

    return available_networks


if __name__ == "__main__":
    print(get_available_network_interfaces())

from dataclasses import dataclass, asdict


@dataclass
class Client:
    name: str
    nickname: str
    mac_address: str
    vendor: str
    connection_time: str


class ClientList(list[Client]):
    def check_if_client_is_connected_by_mac(self, mac: str):
        return _check_if_client_is_connected(self, attribute="mac_address", value=mac)

    def check_if_client_is_connected_by_name(self, name: str):
        return _check_if_client_is_connected(self, attribute="name", value=name)

    def check_if_client_is_connected_by_vendor(self, vendor: str):
        return _check_if_client_is_connected(self, attribute="vendor", value=vendor)

    def as_list_of_dicts(self):
        return [asdict(client) for client in self]


def _check_if_client_is_connected(devices: ClientList, attribute: str, value: str):
    for device in devices:
        if device.__getattribute__(attribute) == value:
            return True

    return False

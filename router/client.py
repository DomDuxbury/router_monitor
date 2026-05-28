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

    def get_laptop_mode(self):
        linux_is_connected = self.check_if_client_is_connected_by_name("cachyos-x8664")
        windows_is_connected = self.check_if_client_is_connected_by_vendor("MSFT 5 0")

        if linux_is_connected:
            return "linux"
        elif windows_is_connected:
            return "windows"
        else:
            return "offline"

    def get_extra_clients_connected(
        self, expected_clients: int, owner_is_home: bool, laptop_mode: bool
    ):
        num_clients_online = len(list(self))

        if owner_is_home:
            expected_clients = expected_clients + 1

        if laptop_mode != "offline":
            expected_clients = expected_clients + 1

        return num_clients_online - expected_clients


def _check_if_client_is_connected(devices: ClientList, attribute: str, value: str):
    for device in devices:
        if device.__getattribute__(attribute) == value:
            return True

    return False

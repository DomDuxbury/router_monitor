from router.client import Client, ClientList


def test_client_list_helpers_and_extra_client_logic():
    clients = ClientList(
        [
            Client("Owner", "Owner", "AA:BB:CC:DD:EE:FF", "ACME", "1"),
            Client("Linux Laptop", "Linux Laptop", "11:22:33:44:55:66", "ACME", "2"),
            Client("Work Laptop", "Work Laptop", "77:88:99:AA:BB:CC", "ACME", "3"),
        ]
    )

    assert clients.check_if_client_is_connected_by_mac("11:22:33:44:55:66") is True
    assert clients.check_if_client_is_connected_by_name("Owner") is True
    assert clients.get_laptop_mode() == "linux"
    assert clients.get_is_work_laptop_connected() is True
    assert (
        clients.get_extra_clients_connected(
            expected_clients=3,
            owner_is_home=False,
            laptop_mode="offline",
            work_laptop_is_connected=False,
        )
        == 0
    )

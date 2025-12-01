# import time
from router import Router, ClientList
import warnings
import configparser

warnings.filterwarnings("ignore")

# from kafka import KafkaProducer
# import json


def is_owner_home(clients: ClientList, phone_mac_address):
    return


def get_laptop_mode(clients: ClientList):
    linux_is_connected = clients.check_if_client_is_connected_by_name("cachyos-x8664")
    windows_is_connected = clients.check_if_client_is_connected_by_vendor("MSFT 5 0")

    if linux_is_connected:
        return "linux"
    elif windows_is_connected:
        return "windows"
    else:
        return "offline"


def get_extra_clients_connected(
    clients: ClientList, owner_is_home: bool, laptop_mode: bool
):
    num_clients_online = len(list(clients))
    expected_clients = 1

    if owner_is_home:
        expected_clients = expected_clients + 1

    if laptop_mode != "offline":
        expected_clients = expected_clients + 1

    return num_clients_online - expected_clients


def main():
    # producer = KafkaProducer(
    #     bootstrap_servers="localhost:9092",
    #     value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    # )

    config = configparser.ConfigParser()
    config.read(".network_config.ini")

    phone_mac_address = config.get("General", "phonename")
    router = Router(config_file=".router_config.ini")

    app_traffic = router.get_app_traffic_24hours()
    print(app_traffic)
    network_traffic = router.get_network_traffic_24hours()
    print(network_traffic)
    clients = router.get_client_info()
    print(clients)

    owner_is_home = clients.check_if_client_is_connected_by_mac(phone_mac_address)
    laptop_mode = get_laptop_mode(clients)
    extra_clients_connected = get_extra_clients_connected(
        clients, owner_is_home, laptop_mode
    )

    print(f"laptop mode: {laptop_mode}")
    print(f"extra clients connected: {extra_clients_connected}")

    if owner_is_home:
        print("Dom is home")
    else:
        print("Dom is not home")

    # if x > 0:
    #     producer.send(
    #         "jsonRouterOutput",
    #         {
    #             "laptop_mode": laptop_mode,
    #             "num_extra_clients": extra_clients_connected,
    #             "owner_is_home": owner_is_home,
    #             "data_download": change_upload,
    #             "data_upload": change_download,
    #         },
    #     )

    # time.sleep(5)


if __name__ == "__main__":
    main()

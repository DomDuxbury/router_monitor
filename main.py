import time
from router import Router, ClientList, DataDelta
from datetime import datetime
import warnings
import configparser


from kafka import KafkaProducer
import json

warnings.filterwarnings("ignore")


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
    expected_clients = 2

    if owner_is_home:
        expected_clients = expected_clients + 1

    if laptop_mode != "offline":
        expected_clients = expected_clients + 1

    return num_clients_online - expected_clients


def main():
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    config = configparser.ConfigParser()
    config.read(".network_config.ini")

    phone_mac_address = config.get("General", "phonename")
    router = Router(config_file=".router_config.ini")

    last_traffic = router.get_all_time_traffic()
    last_read_time = datetime.utcnow()

    for x in range(0, 100000):
        time.sleep(1)

        new_traffic = router.get_all_time_traffic()
        new_read_time = datetime.utcnow()
        download_diff = new_traffic.downloaded_bytes - last_traffic.downloaded_bytes
        upload_diff = new_traffic.uploaded_bytes - last_traffic.uploaded_bytes
        data_delta = DataDelta(
            downloaded_bytes=download_diff,
            uploaded_bytes=upload_diff,
            delta_start=last_read_time,
            delta_end=new_read_time,
            length_secs=0,
        )

        clients = router.get_client_info()
        owner_is_home = clients.check_if_client_is_connected_by_mac(phone_mac_address)
        laptop_mode = get_laptop_mode(clients)
        extra_clients_connected = get_extra_clients_connected(
            clients, owner_is_home, laptop_mode
        )

        producer.send(
            "routerTickData",
            {
                "laptop_mode": laptop_mode,
                "num_extra_clients": extra_clients_connected,
                "clients": clients.as_list_of_dicts(),
                "owner_is_home": owner_is_home,
                "data_download": data_delta.downloaded_bytes,
                "data_upload": data_delta.uploaded_bytes,
                "window_length": data_delta.length_secs,
            },
        )

        last_traffic = new_traffic
        last_read_time = new_read_time


if __name__ == "__main__":
    main()

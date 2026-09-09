import configparser
import json
import sys
import time
import warnings

from kafka import KafkaProducer

from router import Router

warnings.filterwarnings("ignore")


def main(admin: str, password: str, num_ticks: int = 100000):
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    config = configparser.ConfigParser()
    config.read("config.ini")

    phone_mac_address = config.get("General", "phone_mac")
    expected_clients = int(config.get("General", "expected_clients"))
    interval_secs = int(config.get("General", "interval_secs"))

    router = Router(admin, password)

    for x in range(num_ticks):
        time.sleep(interval_secs)

        tick_data = router.get_traffic_data_tick()

        clients = router.get_client_info()

        owner_is_home = clients.check_if_client_is_connected_by_mac(phone_mac_address)
        laptop_mode = clients.get_laptop_mode()
        work_laptop_is_connected = clients.get_is_work_laptop_connected()

        extra_clients_connected = clients.get_extra_clients_connected(
            expected_clients, owner_is_home, laptop_mode, work_laptop_is_connected
        )

        producer.send(
            "routerTickData",
            {
                "laptop_mode": laptop_mode,
                "num_extra_clients": extra_clients_connected,
                "clients": clients.as_list_of_dicts(),
                "owner_is_home": owner_is_home,
                "data_download": tick_data.downloaded_bytes,
                "data_upload": tick_data.uploaded_bytes,
                "window_length": tick_data.length_secs,
            },
        )


if __name__ == "__main__":
    with open(sys.argv[2], "r") as temp_password_file:
        password = temp_password_file.readline().strip()

    main(sys.argv[1], password)

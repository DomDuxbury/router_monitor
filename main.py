import time
from router import Router
import warnings
import configparser
import sys


from kafka import KafkaProducer
import json

warnings.filterwarnings("ignore")


def main(admin: str, password: str):
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

    for x in range(0, 100000):
        time.sleep(interval_secs)

        tick_data = router.get_traffic_data_tick()

        clients = router.get_client_info()

        owner_is_home = clients.check_if_client_is_connected_by_mac(phone_mac_address)
        laptop_mode = clients.get_laptop_mode()
        extra_clients_connected = clients.get_extra_clients_connected(
            expected_clients, owner_is_home, laptop_mode
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
    main(sys.argv[1], sys.argv[2])

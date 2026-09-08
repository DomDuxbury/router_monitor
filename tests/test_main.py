from types import SimpleNamespace

import main as main_script
from router.client import Client, ClientList


class FakeConfig:
    def read(self, path):
        return None

    def get(self, section, key):
        values = {
            "phone_mac": "AA:BB:CC:DD:EE:FF",
            "expected_clients": "2",
            "interval_secs": "0",
        }
        return values[key]


class FakeProducer:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.sent = []

    def send(self, topic, payload):
        self.sent.append((topic, payload))


class FakeRouter:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_traffic_data_tick(self):
        return SimpleNamespace(
            downloaded_bytes=500,
            uploaded_bytes=250,
            length_secs=30,
        )

    def get_client_info(self):
        return ClientList(
            [
                Client("Owner", "Owner", "AA:BB:CC:DD:EE:FF", "ACME", "1"),
                Client(
                    "Linux Laptop", "Linux Laptop", "11:22:33:44:55:66", "ACME", "2"
                ),
                Client("Guest One", "Guest One", "00:11:22:33:44:55", "ACME", "3"),
                Client("Guest Two", "Guest Two", "66:77:88:99:AA:BB", "ACME", "4"),
            ]
        )


def test_main_emits_expected_router_tick_data(monkeypatch):
    monkeypatch.setattr(main_script.configparser, "ConfigParser", FakeConfig)
    monkeypatch.setattr(main_script, "KafkaProducer", lambda **kwargs: producer)
    monkeypatch.setattr(main_script, "Router", FakeRouter)
    monkeypatch.setattr(main_script.time, "sleep", lambda seconds: None)

    producer = FakeProducer(bootstrap_servers="localhost:9092")

    main_script.main("admin", "secret", num_ticks=1)

    # Check the producer sent the expected data to the correct topic
    assert producer.sent[0][0] == "routerTickData"

    # Check the payload contains the expected values
    payload = producer.sent[0][1]
    assert payload["owner_is_home"] is True
    assert payload["laptop_mode"] == "linux"
    assert payload["num_extra_clients"] == 0
    assert payload["data_download"] == 500

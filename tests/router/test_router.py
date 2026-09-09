from datetime import UTC, datetime
from types import SimpleNamespace

from router.router import Router
from router.router_data import Data


def test_router_get_traffic_data_tick_updates_state():
    router = Router.__new__(Router)
    router.last_traffic = Data(downloaded_bytes=1000, uploaded_bytes=2000)
    router.last_read_time = datetime(2024, 1, 1, tzinfo=UTC)
    router.get_all_time_traffic = lambda: Data(
        downloaded_bytes=1500, uploaded_bytes=2600
    )

    delta = router.get_traffic_data_tick()

    assert delta.downloaded_bytes == 500
    assert delta.uploaded_bytes == 600
    assert delta.length_secs >= 0
    assert router.last_traffic.downloaded_bytes == 1500
    assert router.last_traffic.uploaded_bytes == 2600


def test_router_get_client_info_parses_api_payload():
    router = Router.__new__(Router)
    payload = (
        b'fromNetworkmapd : [{"maclist":["AA:BB","11:22"],"AA:BB":{"name":"Work Laptop","nickName":"Work Laptop","vendor":"Vendor","wlConnectTime":"1"},'
        b'"11:22":{"name":"Linux Laptop","nickName":"Linux Laptop","vendor":"Vendor","wlConnectTime":"2"}}],\n'
    )
    router._make_api_request = lambda url, extra_headers=None: SimpleNamespace(
        content=payload
    )

    clients = router.get_client_info()

    assert [client.mac_address for client in clients] == ["AA:BB", "11:22"]
    assert clients[0].nickname == "Work Laptop"
    assert clients[0].vendor == "Vendor"
    assert clients[1].nickname == "Linux Laptop"
    assert clients[1].vendor == "Vendor"

from datetime import datetime
from router.router_data import AppData, DeviceData, HourlyData, Data, DataDelta
from router.client import Client, ClientList
import requests
import json
import base64


def login(username: str, password: str) -> str | None:
    url = "https://192.168.50.1:8443/login.cgi"
    authorisation = username + ":" + password
    authorisation_encoding = base64.b64encode(bytes(authorisation, "utf-8"))

    body = {
        "login_authorization": authorisation_encoding,
        "action_wait": 5,
        "current_page": "Main_Login.asp",
        "next_page": "index.asp",
        "login_captcha": None,
        "action_mode": None,
        "action_script": None,
        "group_id": None,
    }

    res = requests.post(
        url,
        headers={
            "Host": "192.168.50.1:8443",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "177",
            "Origin": "https://192.168.50.1:8443",
            "Connection": "keep-alive",
            "Referer": "https://192.168.50.1:8443/Main_Login.asp",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
        },
        data=body,
        verify=False,
    )

    if len(res.cookies) == 0:
        raise SystemExit(ValueError("Error: Wrong Username or Password"))
    else:
        for c in res.cookies:
            cookie = c.value

        print("Login Success")
        return cookie


class Router:
    access_token: str | None
    last_traffic: Data
    last_read_time: datetime

    def __init__(self, username: str, password: str):
        self.access_token = login(username, password)
        self.last_read_time = datetime.utcnow()
        self.last_traffic = self.get_all_time_traffic()

    def _make_api_request(self, url: str, extra_headers={}):
        return requests.get(
            url,
            headers={
                "Cookie": f"asus_s_token={self.access_token}; clickedItem_tab=0",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0",
                **extra_headers,
            },
            verify=False,
        )

    def get_app_traffic_24hours(
        self, client_mac: str = "E8:BF:B8:AB:BD:2D", end_time: datetime = datetime.now()
    ) -> list[AppData]:
        total_seconds = round(int((end_time - datetime(1970, 1, 1)).total_seconds()))
        url = f"https://192.168.50.1:8443/getWanTraffic.asp?client={client_mac}&mode=detail&dura=24&date={total_seconds}"
        res = self._make_api_request(url)
        str_content = res.content.decode("UTF-8").split("\n")[1].split("=")[1]
        json_content = json.loads(str_content.split(";")[0])
        return [
            AppData(dns_group=data[0], uploaded_bytes=data[1], downloaded_bytes=data[2])
            for data in json_content
        ]

    def get_network_traffic_24hours(
        self, end_time: datetime = datetime.now()
    ) -> list[DeviceData]:
        total_seconds = round(int((end_time - datetime(1970, 1, 1)).total_seconds()))
        url = f"https://192.168.50.1:8443/getAppTraffic.asp?client=all&mode=detail&dura=24&date={total_seconds}"
        res = self._make_api_request(url)
        str_content = res.content.decode("UTF-8").split("\n")[1].split("=")[1]
        json_content = json.loads(str_content.split(";")[0])
        return [
            DeviceData(
                mac_address=data[0], uploaded_bytes=data[1], downloaded_bytes=data[2]
            )
            for data in json_content
        ]

    def get_network_traffic_hourly(
        self, end_time: datetime = datetime.now(), device_mac_address: str = "all"
    ) -> list[HourlyData]:
        total_seconds = round(int((end_time - datetime(1970, 1, 1)).total_seconds()))
        current_hour = datetime.now().hour
        url = f"https://192.168.50.1:8443/getWanTraffic.asp?client={device_mac_address}&mode=hour&dura=24&date={total_seconds}"
        res = self._make_api_request(url)
        str_content = res.content.decode("UTF-8").split("\n")[1].split("=")[1]
        json_content = json.loads(str_content.split(";")[0])
        return [
            HourlyData(
                hour_beginning=(i + current_hour) % 24,
                uploaded_bytes=data[0],
                downloaded_bytes=data[1],
                device=device_mac_address,
            )
            for i, data in enumerate(json_content)
        ]

    def get_all_time_traffic(self) -> Data:
        url = "https://192.168.50.1:8443/update.cgi"
        body = {
            "output": "netdev",
        }
        res = requests.post(
            url,
            headers={
                "Cookie": f"asus_s_token={self.access_token}; clickedItem_tab=0",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0",
                "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "keep-alive",
                "Referer": "https://192.168.50.1:8443/Main_TrafficMonitor_realtime.asp",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
            },
            verify=False,
            data=body,
        )
        data = res.content.decode().split("'INTERNET':")[1].split("\n")[0]
        download = int(data.split("rx:")[1].split(",tx:")[0], base=16)
        upload = int(data.split("tx:")[1].split("}")[0], base=16)
        return Data(uploaded_bytes=upload, downloaded_bytes=download)

    def get_client_info(self) -> ClientList:
        url = "https://192.168.50.1:8443/update_clients.asp?_=1764602439985"
        res = self._make_api_request(
            url,
            extra_headers={
                "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "keep-alive",
                "Referer": "https://192.168.50.1:8443/index.asp",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
            },
        )
        str_content = (
            res.content.decode().split("fromNetworkmapd : ")[1].split(",\n")[0]
        )
        json_content = json.loads(str_content)[0]
        return ClientList(
            [
                Client(
                    json_content[mac]["name"],
                    json_content[mac]["nickName"],
                    mac,
                    json_content[mac]["vendor"],
                    json_content[mac]["wlConnectTime"],
                )
                for mac in json_content["maclist"]
            ]
        )

    def get_traffic_data_tick(self) -> DataDelta:
        new_read_time = datetime.utcnow()
        new_traffic = self.get_all_time_traffic()

        download_diff = (
            new_traffic.downloaded_bytes - self.last_traffic.downloaded_bytes
        )
        upload_diff = new_traffic.uploaded_bytes - self.last_traffic.uploaded_bytes

        data_delta = DataDelta(
            downloaded_bytes=download_diff,
            uploaded_bytes=upload_diff,
            delta_start=self.last_read_time,
            delta_end=new_read_time,
            length_secs=0,
        )

        self.last_traffic = new_traffic
        self.last_read_time = new_read_time

        return data_delta

import aiohttp
import asyncio
import time
from asusrouter import AsusRouter, AsusData
from asusrouter.modules.connection import ConnectionState
from kafka import KafkaProducer
import configparser
import json


def configure_router(session):
    config = configparser.ConfigParser()
    config.read(".router_config.ini")

    hostname = config.get("General", "hostname")
    phonename = config.get("General", "phonename")
    username = config.get("Secret", "username")
    password = config.get("Secret", "password")

    return AsusRouter(
        hostname=hostname,
        username=username,
        password=password,
        use_ssl=False,
        session=session,
    ), phonename


def is_owner_home(clients, phonename):
    phonename = "iPhone"
    return check_if_device_is_connected(clients, phonename)


def get_laptop_mode(clients):
    linux_is_connected = check_if_device_is_connected(clients, "cachyos-x8664")
    windows_is_connected = check_if_device_is_connected(clients, "MSFT 5 0")

    if linux_is_connected:
        return "linux"
    elif windows_is_connected:
        return "windows"
    else:
        return "offline"


def check_if_device_is_connected(clients, device_name: str):
    for mac in clients:
        client = clients[mac]
        if (
            client.description.name == device_name
            and client.state is ConnectionState.CONNECTED
        ):
            return True

    return False


def get_extra_clients_connected(clients, owner_is_home, laptop_mode):
    connected_clients = filter(
        lambda client: client.state is ConnectionState.CONNECTED, clients.values()
    )
    num_clients_online = len(list(connected_clients))
    expected_clients = 1

    if owner_is_home:
        expected_clients = expected_clients + 1

    if laptop_mode != "offline":
        expected_clients = expected_clients + 1

    return num_clients_online - expected_clients


def main():
    loop = asyncio.new_event_loop()
    session = aiohttp.ClientSession(loop=loop)
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    router, phonename = configure_router(session)

    # Connect to the router
    loop.run_until_complete(router.async_connect())

    last_in = 0
    last_out = 0

    for x in range(0, 9999999999999):
        res = loop.run_until_complete(router.async_get_data(AsusData.NETWORK))
        total_in = res["bridge"]["rx"]
        total_out = res["bridge"]["tx"]

        change_in = total_in - last_in
        change_out = total_out - last_out
        clients = loop.run_until_complete(router.async_get_data(AsusData.CLIENTS))

        owner_is_home = is_owner_home(clients, phonename)
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

        print(f"data in: {round(change_in / 1000)}kb")
        print(f"data out: {round(change_out / 1000)}kb")

        last_in = total_in
        last_out = total_out

        if x > 0:
            producer.send(
                "jsonRouterOutput",
                {
                    "laptop_mode": laptop_mode,
                    "num_extra_clients": extra_clients_connected,
                    "owner_is_home": owner_is_home,
                    "data_in": change_in,
                    "data_out": change_out,
                },
            )

        time.sleep(5)

    loop.run_until_complete(router.async_disconnect())
    loop.run_until_complete(session.close())


if __name__ == "__main__":
    main()

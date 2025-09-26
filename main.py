import aiohttp
import asyncio
import time
from asusrouter import AsusRouter, AsusData
from asusrouter.modules.connection import ConnectionState
import configparser


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


def is_owner_home(loop, router, phonename):
    # Now you can use the router object to call methods
    clients = loop.run_until_complete(router.async_get_data(AsusData.CLIENTS))

    for mac in clients:
        client = clients[mac]
        if (
            client.description.name == "iPhone-17467328"
            and client.state is not ConnectionState.DISCONNECTED
        ):
            return True

    return False


def main():
    loop = asyncio.new_event_loop()
    session = aiohttp.ClientSession(loop=loop)
    router, phonename = configure_router(session)

    # Connect to the router
    loop.run_until_complete(router.async_connect())

    last_in = 0
    last_out = 0

    for x in range(1, 10):
        res = loop.run_until_complete(router.async_get_data(AsusData.NETWORK))
        total_in = res["bridge"]["rx"]
        total_out = res["bridge"]["tx"]

        change_in = total_in - last_in
        change_out = total_out - last_out
        owner_is_home = is_owner_home(loop, router, phonename)

        if owner_is_home:
            print("Dom is home")
        else:
            print("Dom is not home")

        print(f"data in: {round(change_in / 1000)}kb")
        print(f"data out: {round(change_out / 1000)}kb")

        last_in = total_in
        last_out = total_out

        time.sleep(10)

    loop.run_until_complete(router.async_disconnect())
    loop.run_until_complete(session.close())


if __name__ == "__main__":
    main()

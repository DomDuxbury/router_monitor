from datetime import datetime
import requests
import time


def main():
    for x in range(0, 10):
        now_total_seconds = int((datetime.now() - datetime(1970, 1, 1)).total_seconds())
        now_total_seconds_rounded = round(now_total_seconds)
        print(now_total_seconds_rounded)
        print(1764345643)
        cookie = "aThkepFukDDdGULvB6pTqPi6lybSqAP"
        url = f"https://192.168.50.1:8443/getWanTraffic.asp?client=E8:BF:B8:AB:BD:2D&mode=detail&dura=24&date={now_total_seconds_rounded}"
        res = requests.get(
            url,
            headers={
                "Cookie": f"asus_s_token={cookie}; clickedItem_tab=0",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0",
            },
            verify=False,
        )
        print(res)
        print(res.content)
        time.sleep(1)


if __name__ == "__main__":
    main()

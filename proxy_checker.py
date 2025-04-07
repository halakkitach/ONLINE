# proxy_checker.py
import requests
from bs4 import BeautifulSoup

def get_proxies():
    res = requests.get("https://free-proxy-list.net/")
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", id="proxylisttable")
    proxies = []

    for row in table.tbody.find_all("tr"):
        cols = row.find_all("td")
        ip = cols[0].text
        port = cols[1].text
        https = cols[6].text == "yes"
        if https:
            proxies.append(f"http://{ip}:{port}")
    return proxies

def is_working(proxy):
    try:
        res = requests.get("https://www.dailymotion.com", proxies={
            "http": proxy, "https": proxy
        }, timeout=5)
        return res.status_code == 200
    except:
        return False

def main():
    proxies = get_proxies()
    for proxy in proxies:
        if is_working(proxy):
            # ONLY print this line as output
            print(proxy)
            return
    print("")  # fallback kosong kalau tidak ada proxy valid

if __name__ == "__main__":
    main()

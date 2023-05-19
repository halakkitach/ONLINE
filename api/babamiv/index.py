#!/usr/bin/python3

from urllib.parse import unquote
import requests
import re
import os
import sys

windows = False
if 'win' in sys.platform:
    windows = True

def erorya():
    url = 'http://halakkitach.github.io/ONLINE/erorya'
    m3u8_get = requests.get(f"{url}/index.m3u8").text
    for ts in ['1infoku.m3u8', '2KITA.m3u8']:
        m3u8_get = m3u8_get.replace(ts, f"{url}/{ts}")
    return m3u8_get

def grab(url):
    response = s.get(url, timeout=15).text
    if '.m3u8' not in response:
        return erorya()
    else:
        for code in ['403 ', '404 ', '500 ']:
            if code in response:
                return erorya()
            else:
                break
        return response

s = requests.Session()
result = grab('https://cdn.thomasandi.my.id/chpriv/vid.m3u8?id=' + str(sys.argv[1]))
print(result)

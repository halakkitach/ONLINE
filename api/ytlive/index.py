#!/usr/bin/python3

# Youtube Live to HLS API Python
# Created by:  @halakkita

from urllib.parse import unquote
import argparse
import requests
import re
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-U", "--url", required=True, help="url location")
parser.add_argument("output", nargs="?", help="output file")
args = parser.parse_args()

windows = False
if 'win' in sys.platform:
    windows = True

def nosignal():
    url = 'https://halakkitafree.online/RCTIPLUS/info.m3u8'
    m3u8_get = requests.get(f"{url}/index.m3u8").text
    for ts in ['01.m3u8', '02.m3u8']:
        m3u8_get = m3u8_get.replace(ts, f"{url}/{ts}")
    return m3u8_get

def grab(url):
    try:
        get = s.get(url)

        findstr = r'\"hlsManifestUrl\":\"(.*?)\"\}'
        regex = re.compile(findstr)
        match = regex.findall(get.text)[0]
        decode = unquote(match)

        return s.get(decode).text
    except:
        return erorya()

s = requests.Session()
result = grab(args.url)
if args.output:
    open(args.output, "w").write(result)
else:
    print(result)

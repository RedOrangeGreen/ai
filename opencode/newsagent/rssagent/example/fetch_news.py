#!/usr/bin/env python3
import urllib.request
import xml.etree.ElementTree as ET
import sys

try:
    url = 'http://feeds.bbci.co.uk/news/world/rss.xml'
    with urllib.request.urlopen(url, timeout=10) as response:
        data = response.read()
    
    root = ET.fromstring(data)
    items = root.findall('.//item')[:5]
    
    for item in items:
        title = item.find('title')
        if title is not None and title.text:
            print(title.text)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)

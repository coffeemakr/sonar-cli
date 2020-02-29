
import requests
import hashlib
from bs4 import BeautifulSoup
from clint.textui import progress
from .link import Link
import os.path

def get_links(study_id):
    url=f"https://opendata.rapid7.com/{study_id}/"
    session = requests.Session()

    cache_file = f'{study_id}.html'
    if os.path.isfile(cache_file):
        with open(cache_file) as cache:
            html = BeautifulSoup(cache.read(), "html.parser")
    else:
        r = session.get(url)
        r.raise_for_status()
        with open(cache_file, 'w') as cache:
            cache.write(r.text)
        html = BeautifulSoup(r.text, "html.parser")
    return parse_links_from_html(html, url, study_id)

def parse_links_from_html(html, download_base, study_id):
    for tbody in html.find_all('tbody'):
        for row in tbody.find_all("tr"):
            sha1sum = row.find(class_='sha').string.strip()
            if 'ungated' in row.attrs['class']:
                link = row.find("a")
                filename = row.td.string.strip()
                link = download_base + filename
                yield Link(filename=filename, sha1sum=sha1sum, gated=False, free_link=link, study_id=study_id)
            else:
                filename = row.find(class_='filename').string.strip()
                yield Link(filename=filename, sha1sum=sha1sum, gated=True, study_id=study_id)


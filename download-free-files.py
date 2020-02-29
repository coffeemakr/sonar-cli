from requests_html import HTMLSession
import requests
import requests_cache
import os.path
import argparse
import hashlib
from bs4 import BeautifulSoup
from clint.textui import progress
import click

def get_file_hash(fp, hash):
    while chunk := fp.read(8192):
        hash.update(chunk)
    return hash.hexdigest()

def has_sha1sum(filename, sha1sum):
    if not os.path.isfile(filename):
        return False
    with open(filename, 'rb') as infile:
        file_hash = get_file_hash(infile, hashlib.sha1())
    return file_hash == sha1sum


class Link:
    def __init__(self, filename, sha1sum, gated,  study_id, free_link=None):
        self.filename = filename
        self.sha1sum = sha1sum
        self.gated = gated
        self.free_link = free_link
        self.study_id = study_id

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



@click.group()
def cli():
    pass


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

@cli.command()
@click.argument('study_id', default=False)
@click.option('--failed/--no-failed', default=True, help='Print only failed')
@click.option('--missing/--no-missing', default=False, help='Print missing')
@click.option('--success/--no-success', default=False, help='Print success')
@click.option('--delete/--no-delete', default=False, help='Delete failed')
def check(study_id, failed=True, missing=False, success=False, delete=False):
    '''
    Check downloaded files have correct checksum
    '''
    for link in get_links(study_id):        
        local_path = os.path.join(study_id, link.filename)
        sha1sum = link.sha1sum
        if os.path.isfile(local_path):
            if has_sha1sum(local_path, sha1sum):
                if success:
                    print(f"OK     : {local_path} - {sha1sum}")
            else:
                if failed:
                    print(f"FAIL   : {local_path} - {sha1sum}")
                if delete:
                    print(f"RM     : {local_path}")
                    os.remove(local_path)
        else:
            if missing:
                print(f"MISSING: {local_path}")



def download_file_to_file(download_url, fp):
    
    r = requests.get(download_url, stream=True, allow_redirects=True)
    r.raise_for_status()
    total_length = int(r.headers['Content-Length'])
   
    for chunk in progress.bar(r.iter_content(chunk_size=1024),label=download_url, expected_size=(total_length/1024) + 1): 
        if chunk:
            fp.write(chunk)
            fp.flush()


@cli.command()
@click.argument('study_id', default=False)
@click.option('--continue', default=False, help='Continue incomplete files')
def download(study_id):
    for link in get_links(study_id):
        if link.gated:
            continue
        local_path = os.path.join(study_id, link.filename)
        if os.path.isfile(local_path):
            stat = os.stat(local_path)
            if stat.st_size == 0:
                print(f"Empty file. continuing {local_path}")
            else:
                print(f"skipping existing file {local_path}")
                continue
        
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'wb') as outfile:
            download_file_to_file(link.free_link, outfile)


def main():
    cli()

if __name__ == "__main__":
    main()
import os.path
import hashlib
import requests


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

def download_file_to_file(download_url, fp):
    r = requests.get(download_url, stream=True, allow_redirects=True)
    r.raise_for_status()
    total_length = int(r.headers['Content-Length'])
   
    for chunk in progress.bar(r.iter_content(chunk_size=1024),label=download_url, expected_size=(total_length/1024) + 1): 
        if chunk:
            fp.write(chunk)
            fp.flush()

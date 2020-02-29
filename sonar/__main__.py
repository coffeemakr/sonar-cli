import os.path
import click

from .parser import get_links
from .utils import has_sha1sum, download_file_to_file

@click.group()
def cli():
    pass


@cli.command()
@click.argument('study_id')
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




@cli.command()
@click.argument('study_id')
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


if __name__ == "__main__":
    cli()
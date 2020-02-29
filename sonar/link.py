
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

#!/usr/bin/env python3

import os
import os.path as path
import requests
import urllib.parse as parse
from requests import auth


class Cloud(object):
    LIST_URL = 'http://my.cl.ly/items'

    def __init__(self, username, password):
        self.digest_auth = auth.HTTPDigestAuth(username, password)

    def list_items(self):
        page = 1
        per_page = 5
        while True:
            response = requests.get(self.LIST_URL,
                headers={'Accept': 'application/json'},
                auth=self.digest_auth,
                params=dict(page=page, per_page=per_page)
            )

            if response.ok:
                items = response.json()
                if len(items) > 0:
                    yield items
                if len(items) < per_page:
                    break
                page = page + 1
            else:
                raise Exception("Error listing items")

if __name__ == '__main__':
    print('Export beginning.')
    destination = os.getenv("DEST_PATH", default="~/Dropbox/cloudapp")
    un = os.getenv("UN")
    pw = os.getenv("PW")
    cl = Cloud(un, pw)

    print('Listing Items.')
    count = 0

    for items in cl.list_items():
        print('Fetched %s items.' % len(items))
        for item in items:
            download_url = item.get('download_url')
            if download_url:
                r = requests.get(download_url, stream=True)

                url = parse.urlparse(download_url)
                filename = url.path.rsplit('/', 1)[-1]
                dest = path.expanduser(destination)
                dest_filename = "%s/%s" % (dest, filename)

                with open(dest_filename, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)

                print("Downloaded to %s" % dest_filename)

            else:
                print('no download url')

        # count = count + 1
        # if count == 4:
        #     break

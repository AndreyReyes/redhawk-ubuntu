#!/usr/bin/python
# Author: Thomas Goodwin <btgoodwin@geontech.com>

import urllib2
import json
import os
import sys
import platform
import re


def download_asset(path, url):
    asset_path = None

    try:
        file_name = os.path.basename(url)
        asset_path = os.path.join(path, file_name)

        if os.path.exists(asset_path):
            # Skip downloading
            asset_path = None
        else:
            if not os.path.exists(path):
                os.makedirs(path)

            f = urllib2.urlopen(url)
            with open(asset_path, "wb") as local_file:
                local_file.write(f.read())
    except BaseException as e:
        sys.exit('Failed to fetch IDE. Error trace: {0}'.format(e))

    return asset_path


def get_target_architecture():
    plataform_architecture = None
    try:
        plataform_architecture = platform.architecture()[0]
    except BaseException as e:
        sys.exit(
                'Could not get architecture from the system.'
                + 'Error traceback: {}'.format(e)
                )
    if '32' in plataform_architecture:
        plataform_architecture = 'x86'
    elif '64' in plataform_architecture:
        plataform_architecture = 'x86_64'
    return plataform_architecture


def handle_release_assets(assets):
    ide_asset = None
    try:
        target_architecture = get_target_architecture()
    except BaseException as e:
        sys.exit(e)

    assets = [
            asset for asset in assets if re.match(
                r'redhawk-ide.+?(?=' + target_architecture + '\.)',
                asset['name']
                )
            ]
    if not assets:
        sys.exit('Failed to find the IDE asset.')
    elif len(assets) > 1:
        sys.exit('Found too many IDE assets matching that description.')

    try:
        ide_asset = download_asset(
                'downloads', assets[0]['browser_download_url']
                )
    except BaseException as e:
        sys.exit(e)
    return ide_asset


def run(pv):
    RELEASES_URL = 'http://api.github.com/repos/RedhawkSDR/redhawk/releases'
    ide_asset = ''

    try:
        releases = json.loads(urllib2.urlopen(RELEASES_URL).read())
        releases = [r for r in releases if r['tag_name'] == pv]
    except BaseException as e:
        sys.exit(e)

    try:
        ide_asset = handle_release_assets(releases[0]['assets'])
    except BaseException as e:
        sys.exit(e)
    return ide_asset

if __name__ == '__main__':
    # First argument is the version
    asset = None
    try:
        asset = run(sys.argv[1])
    except BaseException as e:
        sys.exit(e)
    finally:
        print(asset)

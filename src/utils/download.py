''' This module is a download helper. '''

import sys
import hashlib
import datetime

from urllib.request import urlopen

def print_progress(dl: int, total_length: int, speed: float, display_name: str) -> None:
    '''
    Prints the downloading progress bar to stdout.

    :param int dl: Current downloaded size
    :param int total_length: Size of the file
    :param int speed: Current downloading rate
    :param str display_name: Name of the file to display

    :return: None
    '''

    total_length_kb = int(total_length / 1024)
    total_length_mb = int(total_length / 1024 / 1024)

    speed_kb = int(speed / 1024)
    speed_mb = int(speed / 1024 / 1024)

    total_length_display = ''

    if total_length_mb > 0:
        total_length_display = str(total_length_mb) + 'M'
    else:
        total_length_display = str(total_length_kb) + 'K'

    dl_kb = int(dl / 1024)
    dl_mb = dl / 1024 / 1024

    dl_display = ''
    speed_display = ''

    # Set a convenient display for download size display and speed rate

    if total_length_mb > 0:
        dl_display = str(int(dl_mb)) + 'M'
    else:
        dl_display = str(int(dl_kb)) + 'K'

    if speed_mb > 0:
        speed_display = str(speed_mb) + 'M/s'
    else:
        speed_display = str(speed_kb) + 'K/s'

    done = int(50 * dl / total_length)

    # Display the progress bar

    sys.stdout.write(
        f"\x1b[1K\r{display_name} [%s%s] "
        f"({dl_display}/{total_length_display} - {speed_display})"
        % ('=' * done, ' ' * (50-done))
    )
    sys.stdout.flush()

def download(url: str, file: str, total_length: int = 0, display_name: str = '') -> str:
    '''
    Downloads a file.

    :param str url: URL of the file to download
    :param str file: Destination path
    :param int total_length: Size of the file
    :param str display_name: Name to display while downloading

    :return: MD5 hash of the downloaded file
    :rtype: str
    '''

    if display_name == '':
        display_name = url

    # Initialize md5 hash

    hash_md5 = hashlib.md5()

    # Initialize request

    with urlopen(url) as req:
        chunk_size = 2 * 1024 * 1024
        dl = 0

        start_time = datetime.datetime.now()
        end_time = start_time
        diff = end_time - start_time

        # Download the file

        with open(file, 'wb') as f:
            while True:
                start_time = datetime.datetime.now()

                if diff.total_seconds() > 0:
                    speed = chunk_size / diff.total_seconds()
                else:
                    speed = 0

                dl += chunk_size

                dl = min(dl, total_length)

                chunk = req.read(chunk_size)
                if not chunk:
                    break

                f.write(chunk)

                if total_length != 0:
                    print_progress(dl, total_length, speed, display_name)

                end_time = datetime.datetime.now()
                diff = end_time - start_time

                # Update md5 hash

                hash_md5.update(chunk)

    return hash_md5.hexdigest()

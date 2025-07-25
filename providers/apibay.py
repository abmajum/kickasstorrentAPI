import aiohttp
import math
import datetime

trackers = [
    "udp://tracker.coppersurfer.tk:6969/announce",
    "udp://tracker.openbittorrent.com:6969/announce",
    "udp://9.rarbg.to:2710/announce",
    "udp://9.rarbg.me:2780/announce",
    "udp://9.rarbg.to:2730/announce",
    "udp://tracker.opentrackr.org:1337",
    "http://p4p.arenabg.com:1337/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://tracker.tiny-vps.com:6969/announce",
    "udp://open.stealth.si:80/announce",
]

separator = "&tr="
all_trackers = separator.join(trackers)

def humanbytes(B):
    """Return the given bytes as a human friendly KB, MB, GB, or TB string."""
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)
    GB = float(KB ** 3)
    TB = float(KB ** 4)

    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B / MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B / GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B / TB)

async def get_piratebay_torrents(query_term: str, page: int):
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
    }
    url = f"https://apibay.org/q.php?q={query_term}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()

            for each_item in data:
                try:
                    size = humanbytes(each_item['size'])
                    age = datetime.datetime.fromtimestamp(int(each_item['added'])).strftime('%Y-%m-%d %H:%M:%S')
                    seeds = int(each_item['seeders'])

                    result = {
                        "title": each_item['name'],
                        "hash": each_item['info_hash'],
                        "size": size,
                        "uploader": each_item['username'],
                        "age": age,
                        "seeds": seeds,
                        "magnet": f"magnet:?xt=urn:btih:{each_item['info_hash']}&dn={each_item['name']}&tr={all_trackers}",
                    }

                    results.append(result)
                except Exception as e:
                    # Skip malformed items
                    continue

    sorted_data = sorted(results, key=lambda x: x["seeds"], reverse=True)
    total_pages = 1  # apibay.org doesn't support pagination
    return sorted_data, total_pages

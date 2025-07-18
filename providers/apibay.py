import requests
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
separator="&tr="
all_trackers=separator.join(trackers)

def humanbytes(B):
    """Return the given bytes as a human friendly KB, MB, GB, or TB string."""
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2) # 1,048,576
    GB = float(KB ** 3) # 1,073,741,824
    TB = float(KB ** 4) # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B / MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B / GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B / TB)

def get_piratebay_torrents(query_term: str, page: int):
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    url = f"https://apibay.org/q.php?q={query_term}"
    response = requests.get(url,headers)
    for each_item in response.json():
        result={
            "title": each_item['name'],
            "hash": each_item['info_hash'],            
            "size": humanbytes(each_item['size']),
            "uploader": each_item['username'],
            "age": datetime.datetime.fromtimestamp(int(f"{each_item['added']}")).strftime('%Y-%m-%d %H:%M:%S'),
            "seeds": each_item['seeders'],
            "magnet": f"magnet:?xt=urn:btih:{each_item['info_hash']}&dn={each_item['name']}&tr={all_trackers}",
        }
        results.append(result)
    sorted_data = sorted(results, key=lambda x: int(x["seeds"]), reverse=True)
    total_pages = 1
    return sorted_data, total_pages
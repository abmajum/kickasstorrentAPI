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

def get_piratebay_torrents(query_term: str, page: int):
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    url = f"https://apibay.org/q.php?q={query_term}"
    response = requests.get(url,headers)
    for each_item in response.json():
        result={
            "name": each_item['name'],
            "hash": each_item['info_hash'],
            "uploader": each_item['username'],
            "seeds": each_item['seeders'],
            "size": each_item['size'],
            "date": f"datetime.datetime.fromtimestamp(int({each_item['added']})).strftime('%Y-%m-%d %H:%M:%S')",
            "magnet": f"magnet:?xt=urn:btih:{each_item['info_hash']}&dn={each_item['name']}&tr={all_trackers}",
        }
        results.append(result)
    sorted_data = sorted(results, key=lambda x: int(x["seeds"]), reverse=True)
    total_pages = 1
    return sorted_data, total_pages
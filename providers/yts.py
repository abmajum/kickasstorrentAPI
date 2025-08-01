import aiohttp
import math


trackers = [
"udp://glotorrents.pw:6969/announce",
"udp://tracker.opentrackr.org:1337/announce",
"udp://torrent.gresille.org:80/announce",
"udp://tracker.openbittorrent.com:80",
"udp://tracker.coppersurfer.tk:6969",
"udp://tracker.leechers-paradise.org:6969",
"udp://p4p.arenabg.ch:1337",
"udp://tracker.internetwarriors.net:1337",
"udp://open.demonii.com:1337/announce",
"udp://p4p.arenabg.com:1337"
]
separator="&tr="
all_trackers=separator.join(trackers)

async def get_yts_torrents(query_term: str, page: int):
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    url = f"https://yts.mx/api/v2/list_movies.json?query_term={query_term}&sort_by=seeds&page={page}"
    
    async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()

                if not data.get('data') or not data['data'].get('movies'):
                    return [], 0


                for movie in data['data']['movies']:
                    for torrent in movie['torrents']:
                        result={
                            "title": f"{movie['slug']}-{torrent['quality']}-{torrent['type']}-{torrent['video_codec']}",
                            "hash": torrent['hash'],
                            "size": torrent['size'],
                            "uploader": "yts.mx",
                            "age": torrent['date_uploaded'],
                            "seeds": torrent['seeds'],
                            "magnet": f"magnet:?xt=urn:btih:{torrent['hash']}&dn={movie['slug']}-{torrent['quality']}&tr={all_trackers}",
                        }
                        results.append(result)
                movie_count = data['data'].get('movie_count', 0)
                total_pages = math.ceil(movie_count / 20) if movie_count > 20 else 1
                return results, total_pages
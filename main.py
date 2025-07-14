import urllib.parse
from enum import Enum
from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from providers.yts import get_yts_torrents
from providers.apibay import get_piratebay_torrents
from providers.kickasstorrents import get_kickass_torrents


class Providers(str, Enum):
    kickasstorrent = "kickasstorrent"
    yts = "yts"
    thepiratebay = "thepiratebay"

app = FastAPI(
    title="TorrentAPI",
    description='''
    🔍 **TorrentAPI** allows you to search and retrieve torrent data effortlessly.

    ### Features:
    - 🔎 **Search** for torrents by keyword.
    - 📄 **Navigate** through paginated results.
    - 🔗 **Get magnet links** for downloading.

    **Currently supported provider:**
    - 🧲 KickassTorrents

    ---
    👉 **Visit `/docs` to explore and try the API interactively.**
    ''',
    summary="Search torrents and retrieve magnet links with ease.",
    version="0.0.1",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')

@app.get("/get-torrents/{providers}")
def fetch_torrents(providers: Providers, page: int = 1, query: str = Query(..., description="Search term")):
  encoded_query = urllib.parse.quote(query)
  if providers == providers.kickasstorrent:
    results, total_pages = get_kickass_torrents(encoded_query, page)
  elif providers == providers.yts:
     results, total_pages = get_yts_torrents(encoded_query, page)
  elif providers == providers.thepiratebay:
     results, total_pages = get_piratebay_torrents(encoded_query, page)
  else:
     return{"total_pages": None, "results": None, "message": "No correct provider is chosen"}
  return {"total_pages": total_pages, "current_page": page, "results": results}


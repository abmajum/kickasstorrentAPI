import urllib.parse
import requests
from enum import Enum
from fastapi import FastAPI, Query, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from random import randint
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager

from providers.yts import get_yts_torrents
from providers.apibay import get_piratebay_torrents
from providers.kickasstorrents import get_kickass_torrents
from providers.eztv import get_eztv_torrents

class Providers(str, Enum):
    kickasstorrent = "kickasstorrent"
    yts = "yts"
    thepiratebay = "thepiratebay"
    eztv = "eztv"
API_BASEURL = "https://scrapetorrents-dev.onrender.com"

async def check_site_status():
    response = requests.get(API_BASEURL)
    if response.status_code != 200:
        print(f"API is not running, status_code: {response.status_code}")
    else:
       print(f"API is running, status_code: {response.status_code}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    # repeat task every 10 seconds
    scheduler.add_job(func=check_site_status, trigger='interval', seconds=30)
    scheduler.start()
    yield

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
    - 🧲 YTS
    - 🧲 ThePirateBay
    - 🧲 EZTV

    ---
    👉 **Visit `/docs` to explore and try the API interactively.**
    ''',
    summary="Search torrents and retrieve magnet links with ease.",
    version="0.0.1",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    lifespan=lifespan
)
app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Allow all origins
    allow_credentials=False,      # Must be False when using "*"
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)

# @app.get("/", include_in_schema=False)
# async def docs_redirect():
#     return RedirectResponse(url='/docs')
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "kickasstorrents, yts, piratbay, eztv"})



@app.get("/get-torrents/{providers}")
async def fetch_torrents(providers: Providers, page: int = 1, query: str = Query(..., description="Search term")):
    encoded_query = urllib.parse.quote(query)
    if providers == providers.kickasstorrent:
        results, total_pages = await get_kickass_torrents(encoded_query, page)
    elif providers == providers.yts:
        results, total_pages = await get_yts_torrents(encoded_query, page)
    elif providers == providers.thepiratebay:
        results, total_pages = await get_piratebay_torrents(encoded_query, page)
    elif providers == providers.eztv:
        results, total_pages = await get_eztv_torrents(encoded_query, page)
    else:
        return{"total_pages": None, "results": None, "message": "No correct provider is chosen"}
    return {"total_pages": total_pages, "current_page": page, "results": results}


# kickasstorrentAPI
A restapi to search torrents and get magnet links. Under the hood it is scraping the website to get necessary details.

# How to run
- Clone the repo
- cd to the repi ```cd kickasstorrentAPI```
- create a virtual env and activate it
  ```
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- Install dependencies ```pip3 install -r requirements.txt```
- run the api for dev env use these flags ```--reload --log-level debug```
- for prod env ```uvicorn main:app --port 3000 --host 0.0.0.0```

import time
import requests
from bs4 import BeautifulSoup
import re
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session(retries=5, backoff_factor=1):
    request_session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    request_session.mount("https://", adapter)

    return request_session

with open("moves.json", "a") as f:
    f.write('[\n')

    for game_id in range(22282, 22620):
        print(f'game id: {game_id}')
        session = create_session(backoff_factor=3)

        game_response = session.get(f'https://www.checkercruncher.com/games/{game_id}', timeout=10)
        game_response.raise_for_status()

        game_text = game_response.text
        game_soup = BeautifulSoup(game_text, 'html.parser')
        scripts = game_soup.find_all("script")
        script = scripts[2]

        match = re.search(r'\[.*?]', script.string)
        if match:
            array_str = match.group(0)
            moves = json.loads(array_str)

            f.write(json.dumps(moves, ensure_ascii=False) + ',\n')

        if game_id % 15 == 0:
            time.sleep(5)

    f.write(']')

print("parsing is done")
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

def js_to_json(js_text):
    js_text = js_text.replace("false", "false")  # JSON compatible
    js_text = js_text.replace("true", "true")
    js_text = js_text.replace("null", "null")
    return js_text

with open("../games.csv", "a") as f:
    for game_id in range(22338, 22620):

        print(f'game id: {game_id}')
        session = create_session(backoff_factor=3)

        game_response = session.get(f'https://www.checkercruncher.com/games/{game_id}', timeout=10)
        game_response.raise_for_status()

        game_text = game_response.text
        game_soup = BeautifulSoup(game_text, 'html.parser')
        scripts = game_soup.find_all("script")
        script = scripts[2]

        gon_dict = {}

        pattern = re.compile(r'gon\.(\w+)\s*=\s*(.*?);', re.DOTALL)
        for key, value in pattern.findall(script.string):
            value = value.strip()
            # If value starts with { or [, treat as JSON
            if value.startswith('{') or value.startswith('['):
                # Make JSON compatible
                value_json = js_to_json(value)
                gon_dict[key] = json.loads(value_json)
            else:
                # Remove quotes for strings
                if value.startswith('"') and value.endswith('"'):
                    gon_dict[key] = value[1:-1]
                elif value in ["true", "false"]:
                    gon_dict[key] = value == "true"
                else:
                    # numbers
                    try:
                        gon_dict[key] = int(value)
                    except ValueError:
                        try:
                            gon_dict[key] = float(value)
                        except ValueError:
                            gon_dict[key] = value

        print(gon_dict['moves'])
        print(gon_dict['game']['black_win'])
        print(gon_dict['game']['white_win'])
        print(gon_dict['position']['board'])    ######rrrrrrrr#rrrr0000#0000wwww#wwwwwwww#####
        print(gon_dict['position']['white_to_play'])

        game_result = 'draw'
        if gon_dict['game']['black_win']:
            game_result = 'black_win'
        if gon_dict['game']['white_win']:
            game_result = 'white_win'

        moves = gon_dict['moves']
        result_string = ",".join(moves)
        board = gon_dict['position']['board']

        f.write(f"{game_id};{game_result};{result_string};{board}\n")
        f.flush()

print("parsing is done")
import requests
from bs4 import BeautifulSoup
import re
import json



with open("moves.json", "w") as f:
    f.write('[\n')

    for page in range(1, 1508):
        print("current page:", page)

        url = "https://www.checkercruncher.com/games?page=" + str(page)

        response = requests.get(url)
        response.raise_for_status()  # raise an error if request failed
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        total_links = len(soup.find_all("a"))
        print("total games:", total_links)
        idx = 1

        for link in soup.find_all("a"):
            print("current link:", idx)
            href = link.get("href")

            if "games" in href:
                response = requests.get('https://www.checkercruncher.com' + href)
                response.raise_for_status()
                game_page = response.text

                page_soup = BeautifulSoup(game_page, 'html.parser')
                tables = page_soup.find_all("table")

                for table in tables:
                    for row in table.find_all("tr"):
                        cells = row.find_all(["td", "th"])
                        cell = cells[0]
                        hyperlink = cell.find("a")
                        if hyperlink:
                            game_ref = hyperlink.get("href")

                            if game_ref and "games" in game_ref:
                                game_response = requests.get('https://www.checkercruncher.com/' + game_ref)
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

            idx += 1

    f.write(']')

# https://www.checkercruncher.com/games
# https://www.checkercruncher.com/games?page=2
# https://www.checkercruncher.com/games/1
# https://www.checkercruncher.com/games/16
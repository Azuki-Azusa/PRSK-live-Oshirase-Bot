import requests
from bs4 import BeautifulSoup


# Get latest 3 lives
def gerLatestLive():
    url = "https://pjsekai.com/?9513417021"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", {"id": "sortable_table1"})

    rows = table.find_all("tr")

    return [(cells[0].text, cells[1].text, cells[3].text) for cells in [row.find_all("td") for row in rows[1:4]]]
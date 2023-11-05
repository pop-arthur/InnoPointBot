import json

import requests
from bs4 import BeautifulSoup
from datetime import datetime


class Parser:
    def __init__(self):
        with open("events.json", "r") as file:
            self.events = json.loads(file.read())

    def save_current_events(self):
        self.events = self.get_current_events()
        with open("events.json", "w") as file:
            file.write(json.dumps(self.events, indent=4, sort_keys=True, default=str))

    def get_updates(self):
        new_events = self.get_current_events()

        diff = list(filter(lambda event: event not in self.events, new_events))
        if diff:
            self.save_current_events()
            return self.get_events_to_str(diff)
        else:
            return "No new events"

    def get_current_events(self) -> list[dict]:
        page = requests.get("https://ipts.innopolis.university/projects")

        if not page.status_code == 200:
            raise ConnectionError

        soup = BeautifulSoup(page.content.decode('utf-8'), "html.parser")
        soup_cards = soup.findAll('div', class_='project-card svelte-1rbeb6e')

        cards = list()
        date_start: datetime = datetime(2000, 1, 1)
        date_end: datetime = datetime(2000, 1, 1)
        card: dict = {}

        for soup_card in soup_cards:
            name: str = soup_card.find('div', class_='title svelte-1rbeb6e').text
            date_str: str = soup_card.find('div', class_='labeled svelte-1e93u8e').text.split("\n")[4].strip()
            date_lst: list[str] = date_str.split("–")

            try:
                if len(date_lst) == 1:
                    date_start = datetime.strptime(date_lst[0].strip() + " " + str(datetime.today().year), "%b %d %Y")
                    card = {"name": name,
                            "date": [date_start]}

                elif len(date_lst) == 2:
                    date_start = datetime.strptime(date_lst[0].strip() + " " + str(datetime.today().year), "%b %d %Y")

                    if date_lst[1].strip().isdigit():
                        date_end = datetime.strptime(
                            str(date_start.month) + " " + date_lst[1].strip() + " " + str(datetime.today().year),
                            "%m %d %Y")
                    else:
                        date_end = datetime.strptime(date_lst[1].strip() + " " + str(datetime.today().year), "%b %d %Y")

                    card = {"name": name,
                            "date": [date_start, date_end]}

                cards.append(card)

            except ValueError:
                pass

        cards = sorted(cards, key=lambda x: x["date"][0])
        return cards

    def get_events_to_str(self, events: list[dict]) -> str:
        past, current, future = [], [], []

        for event in events:
            if len(event["date"]) == 1:
                if (datetime.today().month, datetime.today().day) == (event["date"][0].month, event["date"][0].day):
                    current.append(event)
                elif datetime.today() < event["date"][0]:
                    future.append(event)
                elif event["date"][0] < datetime.today():
                    past.append(event)

            elif len(event["date"]) == 2:
                if event["date"][0] <= datetime.today() <= event["date"][1]:
                    current.append(event)
                elif datetime.today() < event["date"][0]:
                    future.append(event)
                elif event["date"][1] < datetime.today():
                    past.append(event)

        past_str = []
        for event in past:
            if len(event["date"]) == 1:
                past_str.append(" : ".join((event["name"], event["date"][0].strftime("%b %d"))))
            elif len(event["date"]) == 2:
                past_str.append(" : ".join((event["name"], " - ".join(
                    (event["date"][0].strftime("%b %d"), event["date"][1].strftime("%b %d"))))))
        past_str = "Past\n" + "\n".join(past_str)

        current_str = []
        for event in current:
            if len(event["date"]) == 1:
                current_str.append(" : ".join((event["name"], event["date"][0].strftime("%b %d"))))
            elif len(event["date"]) == 2:
                current_str.append(" : ".join((event["name"], " - ".join(
                    (event["date"][0].strftime("%b %d"), event["date"][1].strftime("%b %d"))))))
        current_str = "\nCurrent\n" + "\n".join(current_str)

        future_str = []
        for event in future:
            if len(event["date"]) == 1:
                future_str.append(" : ".join((event["name"], event["date"][0].strftime("%b %d"))))
            elif len(event["date"]) == 2:
                future_str.append(" : ".join((event["name"], " - ".join(
                    (event["date"][0].strftime("%b %d"), event["date"][1].strftime("%b %d"))))))
        future_str = "\nFuture\n" + "\n".join(future_str)

        return "\n".join((past_str, current_str, future_str))

import json
import os
import time
from datetime import datetime, timedelta
import queue
from sys import platform
import threading
from time import sleep
from EDlogger import logger
from WindowsKnownPaths import *


class MarketParser:
    def __init__(self, file_path=None):
        if platform != "win32":
            self.file_path = file_path if file_path else "./linux_ed/Market.json"
        else:
            from WindowsKnownPaths import get_path, FOLDERID, UserHandle

            self.file_path = file_path if file_path else (get_path(FOLDERID.SavedGames, UserHandle.current)
                                                          + "/Frontier Developments/Elite Dangerous/Market.json")

        self.current_data = self.get_market_data()
        self.sellable_items = self.get_sellable_items()
        self.buyable_items = self.get_buyable_items()


        # self.watch_thread = threading.Thread(target=self._watch_file_thread, daemon=True)
        # self.watch_thread.start()
        # self.status_queue = queue.Queue()

    # def _watch_file_thread(self):
    #     backoff = 1
    #     while True:
    #         try:
    #             self._watch_file()
    #         except Exception as e:
    #             logger.error('An error occurred when reading status file')
    #             sleep(backoff)
    #             logger.debug('Attempting to restart status file reader after failure')
    #             backoff *= 2
    #
    # def _watch_file(self):
    #     """Detects changes in the Status.json file."""
    #     while True:
    #         status = self.get_cleaned_data()
    #         if status != self.current_data:
    #             self.status_queue.put(status)
    #             self.current_data = status
    #         sleep(1)

    def get_market_data(self):
        """Loads data from the JSON file and returns the data.
        {
        "timestamp": "2024-09-21T14:53:38Z",
        "event": "Market",
        "MarketID": 129019775,
        "StationName": "Rescue Ship Cornwallis",
        "StationType": "MegaShip",
        "StarSystem": "V886 Centauri",
        "Items": [
            {
                "id": 128049152,
                "Name": "$platinum_name;",
                "Name_Localised": "Platinum",
                "Category": "$MARKET_category_metals;",
                "Category_Localised": "Metals",
                "BuyPrice": 3485,
                "SellPrice": 3450,
                "MeanPrice": 58272,
                "StockBracket": 0,
                "DemandBracket": 0,
                "Stock": 0,
                "Demand": 0,
                "Consumer": false,
                "Producer": false,
                "Rare": false
            }, { etc. } ]
        """

        backoff = 1
        while True:
            try:
                with open(self.file_path, 'r') as file:
                    data = json.load(file)
                    break
            except Exception as e:
                logger.error('An error occurred when reading status file')
                sleep(backoff)
                logger.debug('Attempting to restart status file reader after failure')
                backoff *= 2

        self.current_data = data
        #print(json.dumps(data, indent=4))
        return data

    def get_file_modified_time(self) -> float:
        return os.path.getmtime(self.file_path)

    def get_sellable_items(self):
        """ Get a list of items that can be sold to the station.
        {
            "id": 128049154,
            "Name": "$gold_name;",
            "Name_Localised": "Gold",
            "Category": "$MARKET_category_metals;",
            "Category_Localised": "Metals",
            "BuyPrice": 49118,
            "SellPrice": 48558,
            "MeanPrice": 47609,
            "StockBracket": 2,
            "DemandBracket": 0,
            "Stock": 89,
            "Demand": 1,
            "Consumer": true,
            "Producer": false,
            "Rare": false
        }
        """
        data = self.current_data
        self.sellable_items = [x for x in data['Items'] if x['Consumer']]
        # print(json.dumps(newlist, indent=4))
        return self.sellable_items

    def get_buyable_items(self):
        """ Get a list of items that can be bought from the station.
        {
            "id": 128049154,
            "Name": "$gold_name;",
            "Name_Localised": "Gold",
            "Category": "$MARKET_category_metals;",
            "Category_Localised": "Metals",
            "BuyPrice": 49118,
            "SellPrice": 48558,
            "MeanPrice": 47609,
            "StockBracket": 2,
            "DemandBracket": 0,
            "Stock": 89,
            "Demand": 1,
            "Consumer": false,
            "Producer": true,
            "Rare": false
        }
        """
        data = self.current_data
        self.buyable_items = [x for x in data['Items'] if x['Producer']]
        # print(json.dumps(newlist, indent=4))
        return self.buyable_items

    def get_market_name(self) -> str:
        """ Gets the current market (station) name.
        """
        return self.current_data['StationName']

    def get_item(self, item_name) -> dict[any] | None:
        """ Get details of one item. Returns the item detail as below, or None if item does not exist.
        {
            "id": 128049154,
            "Name": "$gold_name;",
            "Name_Localised": "Gold",
            "Category": "$MARKET_category_metals;",
            "Category_Localised": "Metals",
            "BuyPrice": 49118,
            "SellPrice": 48558,
            "MeanPrice": 47609,
            "StockBracket": 2,
            "DemandBracket": 0,
            "Stock": 89,
            "Demand": 1,
            "Consumer": false,
            "Producer": true,
            "Rare": false
        }
        """
        for good in self.current_data['Items']:
            if good['Name_Localised'].upper() == item_name.upper():
                # print(json.dumps(good, indent=4))
                return good

        return None

    def can_buy_item(self, item_name: str) -> bool:
        """ Can the item be bought from the market (is it sold and is there stock). """
        good = self.get_item(item_name)
        if good is None:
            return False

        return good['Producer'] and good['Stock'] > 0

    def can_sell_item(self, item_name: str) -> bool:
        """ Can the item be sold to the market (is it bought and is there demand). """
        good = self.get_item(item_name)
        if good is None:
            return False

        return good['Consumer'] and good['Demand'] > 0


# Usage Example
if __name__ == "__main__":
    parser = MarketParser()
    while True:
        cleaned_data = parser.get_market_data()

        #item = parser.get_item('water')
        sell = parser.can_sell_item('water')
        #buy = parser.can_buy_item('water')

        print(f"Mod Time: {parser.get_file_modified_time()}")
        print(f"Curr Time: {time.time()}")
        print(f"Sell water: {sell}")
        # print(json.dumps(cleaned_data, indent=4))

        time.sleep(1)

import json
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

        self.current_status = self.get_cleaned_data()

    def get_cleaned_data(self):
        """Loads data from the JSON file and returns the data."""
        with open(self.file_path, 'r') as file:
            data = json.load(file)

        return data

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
        data = self.get_cleaned_data()
        new_list = [x for x in data['Items'] if x['Consumer']]
        # print(json.dumps(newlist, indent=4))
        return new_list

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
        data = self.get_cleaned_data()
        new_list = [x for x in data['Items'] if x['Producer']]
        # print(json.dumps(newlist, indent=4))
        return new_list

# Usage Example
if __name__ == "__main__":
    parser = MarketParser()
    cleaned_data = parser.get_cleaned_data()
    print(json.dumps(cleaned_data, indent=4))
    time.sleep(1)

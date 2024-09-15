from time import sleep
from OCR import OCR

"""
File:StationServicesInShip.py    

Description:
  TBD 

Author: Stumpii
"""


class StationServicesInShip:
    def __init__(self, screen, keys):
        self.screen = screen
        self.ocr = OCR(screen)
        self.keys = keys
        self.passenger_lounge = PassengerLounge(self, self.ocr, self.keys)
        self.commodities_market = CommoditiesMarket(self, self.ocr, self.keys)

        self.using_screen = True  # True to use screen, false to use an image. Set screen_image to the image
        self.screen_image = None  # Screen image captured from screen, or loaded by user for testing.

    def goto_station_services(self) -> bool:
        """ Goto Station Services. """
        # Go down to station services and select
        self.keys.send("UI_Back", repeat=5)  # make sure back in ship view
        self.keys.send("UI_Up", repeat=3)  # go to very top (refuel)
        # self.keys.send("UI_Left", hold=1)  # go to very left (refuel)

        self.keys.send("UI_Down")  # station services
        self.keys.send("UI_Select")  # station services
        sleep(3)  # give time for station services to come up
        return True

    def goto_select_mission_board(self) -> bool:
        """ Go to the Mission Board. Shows 3 buttons: COMMUNITY GOALS, MISSION BOARD and PASSENGER LOUNGE. """
        # Go down to station services
        res = self.goto_station_services()
        if not res:
            return False

        # Select Mission Board
        self.keys.send("UI_Up")
        self.keys.send("UI_Left", hold=2)

        self.keys.send("UI_Select")  # select Mission Board
        return True

    def goto_commodities_market(self) -> bool:
        """ Go to the Mission Board. Shows COMMUNITY GOALS, MISSION BOARD and PASSENGER LOUNGE. """
        # Go down to station services
        res = self.goto_station_services()
        if not res:
            return False

        # Select Mission Board
        self.keys.send("UI_Up")  # Is up needed?
        self.keys.send("UI_Left", hold=2)

        self.keys.send("UI_Right")  # Commodities Market
        sleep(0.1)
        self.keys.send("UI_Select")  # Commodities Market
        sleep(1)
        return True

    def goto_mission_board(self) -> bool:
        """ Go to the passenger lounge menu. """
        res = self.goto_select_mission_board()
        if not res:
            return False

        # Select Mission Board
        self.keys.send("UI_Select")  # Mission Board
        sleep(1)  # give time to bring up menu
        return True

    def hide_station_services(self):
        """ Hides station services
        """
        self.keys.send("UI_Back", repeat=5)
        self.keys.send("HeadLookReset")

    def goto_passenger_lounge(self) -> bool:
        """ Go to the passenger lounge menu. """
        res = self.goto_select_mission_board()
        if not res:
            return False

        # Select Passenger Lounge
        self.keys.send("UI_Right")  # Passenger lounge
        sleep(0.1)
        self.keys.send("UI_Select")
        sleep(1)  # give time to bring up menu
        return True


class PassengerLounge:
    def __init__(self, station_services_in_ship, ocr, keys):
        self.parent = station_services_in_ship
        self.ocr = ocr
        self.keys = keys

        self.reg = {}
        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        # Nav Panel region covers the entire navigation panel.
        self.reg['missions'] = {'rect': [0.50, 0.72, 0.65, 0.85]}  # Fraction with ref to the screen/image
        self.reg['mission_dest_col'] = {'rect': [0.47, 0.42, 0.64, 0.82]}  # Fraction with ref to the screen/image
        self.reg['complete_mission_col'] = {'rect': [0.47, 0.25, 0.67, 0.82]}  # Fraction with ref to the screen/image

    def goto_personal_transport_missions(self) -> bool:
        """ Go to the passenger lounge menu. """
        res = self.parent.goto_passenger_lounge()
        if not res:
            return False

        # Select Personal Transportation
        self.keys.send("UI_Up", repeat=3)
        sleep(0.2)
        self.keys.send("UI_Down", repeat=2)
        sleep(0.2)
        self.keys.send("UI_Select")  # select Personal Transport
        # TODO - use OCR to check if the screen it up instead of waiting
        sleep(15)  # wait 15 second for missions menu to show up
        return True

    def goto_complete_missions(self) -> bool:
        """ Go to the passenger lounge menu. """
        res = self.parent.goto_passenger_lounge()
        if not res:
            return False

        # Go to Complete Mission
        self.keys.send("UI_Right", repeat=2)
        self.keys.send("UI_Select")
        return True

    def find_mission_to_complete(self) -> bool:
        """ Find the first mission in the completed missions list.
        True if a completed mission is selected, else False (no missions left to turn in). """
        return self.ocr.select_item_in_list("COMPLETE MISSION", self.reg['complete_mission_col'])

    def missions_ready_to_complete(self) -> bool:
        """ Check if the COMPLETE MISSIONS button is enabled (we have missions to turn in.
        True if there are missions, else False. """
        return self.ocr.is_text_in_region("COMPLETE MISSIONS", self.reg['missions'])

    def select_mission_with_dest(self, dest) -> bool:
        """ Select a mission with the required destination.
        True if there are missions, else False. """
        return self.ocr.select_item_in_list(dest, self.reg['mission_dest_col'])


class CommoditiesMarket:
    def __init__(self, station_services_in_ship, ocr, keys):
        self.parent = station_services_in_ship
        self.ocr = ocr
        self.keys = keys

        self.reg = {}
        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        # Nav Panel region covers the entire navigation panel.
        self.reg['cargo_col'] = {'rect': [0.13, 0.25, 0.19, 0.86]}  # Fraction with ref to the screen/image
        self.reg['commodity_name_col'] = {'rect': [0.19, 0.25, 0.41, 0.86]}  # Fraction with ref to the screen/image
        self.reg['supply_demand_col'] = {'rect': [0.42, 0.25, 0.49, 0.86]}  # Fraction with ref to the screen/image

    def select_buy(self) -> bool:
        """ Select Buy. Assumes on Commodities Market screen. """

        # Select Buy
        self.keys.send("UI_Left", repeat=2)
        self.keys.send("UI_Up", repeat=4)

        self.keys.send("UI_Select")  # Select Buy
        return True

    def select_sell(self) -> bool:
        """ Select Buy. Assumes on Commodities Market screen. """

        # Select Buy
        self.keys.send("UI_Left", repeat=2)
        self.keys.send("UI_Up", repeat=4)

        self.keys.send("UI_Down")
        self.keys.send("UI_Select")  # Select Sell
        return True

    def buy_commodity(self, name, qty) -> bool:
        """ Buy qty of commodity. If qty >= 9999 then buy as much as possible. """
        self.select_buy()
        self.keys.send("UI_Right")
        self.keys.send("UI_Up", hold=2)
        found = self.ocr.select_item_in_list(name, self.reg['commodity_name_col'], self.keys)
        if not found:
            return False

        self.keys.send("UI_Select")
        sleep(0.1)
        self.keys.send("UI_Left")
        self.keys.send("UI_Up", repeat=2)

        # Increment count
        if qty >= 9999:
            self.keys.send("UI_Right", hold=5)
        else:
            self.keys.send("UI_Right", repeat=qty)

        self.keys.send("UI_Down")  # To Buy
        self.keys.send("UI_Select")  # Buy

        self.keys.send("UI_Back")

    def sell_commodity(self, name, qty) -> bool:
        """ Sell qty of commodity. If qty >= 9999 then sell as much as possible. """
        self.select_sell()
        self.keys.send("UI_Right")
        self.keys.send("UI_Up", hold=2)
        found = self.ocr.select_item_in_list(name, self.reg['commodity_name_col'], self.keys)
        if not found:
            return False

        self.keys.send("UI_Select")
        sleep(0.1)
        self.keys.send("UI_Left")
        self.keys.send("UI_Up", repeat=2)

        # Increment count
        if qty >= 9999:
            self.keys.send("UI_Right", hold=5)
        else:
            self.keys.send("UI_Right", repeat=qty)

        self.keys.send("UI_Down")  # To Sell
        self.keys.send("UI_Select")  # Sell

        self.keys.send("UI_Back")


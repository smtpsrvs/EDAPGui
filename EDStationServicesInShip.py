import time
from time import sleep

import cv2

from CargoParser import CargoParser
from EDAP_data import GuiFocusNoFocus
from EDlogger import logger
from MarketParser import MarketParser
from OCR import OCR
from Screen_Regions import reg_scale_for_station, size_scale_for_station
from StatusParser import StatusParser

"""
File:StationServicesInShip.py    

Description:
  TBD 

Author: Stumpii
"""


def goto_ship_view(keys, status_parser) -> bool:
    """ Goto ship view. """
    # Go down to ship view
    while not status_parser.get_gui_focus() == GuiFocusNoFocus:
        keys.send("UI_Back")  # make sure back in ship view

    # self.keys.send("UI_Back", repeat=5)  # make sure back in ship view
    keys.send("UI_Up", repeat=3)  # go to very top (refuel line)

    return True


class EDStationServicesInShip:
    def __init__(self, screen, keys, voice):
        self.commodities_at_bottom = False
        self.commodities_in_center = False
        self.commodities_in_right = False
        self.screen = screen
        self.ocr = OCR(screen)
        self.keys = keys
        self.vce = voice
        self.passenger_lounge = PassengerLounge(self, self.ocr, self.keys, self.screen)
        self.commodities_market = CommoditiesMarket(self, self.ocr, self.keys, self.screen)
        self.status = StatusParser()
        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        self.reg = {'connected_to': {'rect': [0.0, 0.0, 0.25, 0.25]},
                    'stn_svc_layout': {'rect': [0.05, 0.40, 0.60, 0.76]},
                    'commodities_market': {'rect': [0.0, 0.0, 0.25, 0.25]}}

    def goto_station_services(self) -> bool:
        """ Goto Station Services. """
        # Go to ship view
        goto_ship_view(self.keys, self.status)
        # self.keys.send("UI_Left", hold=1)  # go to very left (refuel line)

        self.keys.send("UI_Down")  # station services
        self.keys.send("UI_Select")  # station services

        # Scale the regions based on the target resolution.
        scl_reg_rect = reg_scale_for_station(self.reg['connected_to'], self.screen.screen_width, self.screen.screen_height)

        # Wait for screen to appear
        res = self.ocr.wait_for_text(["CONNECTED TO"], scl_reg_rect)

        # Store image
        image = self.screen.get_screen_full()
        cv2.imwrite(f'test/station-services/station-services.png', image)

        return res

    def determine_commodities_location(self) -> bool:
        # Get the services layout as the layout may be different per station
        # There is probably a better way to do this!
        self.commodities_in_center = False
        self.commodities_in_right = False
        self.commodities_at_bottom = False

        # Scale the regions based on the target resolution.
        scl_reg_rect = reg_scale_for_station(self.reg['stn_svc_layout'], self.screen.screen_width, self.screen.screen_height)

        image = self.ocr.capture_region(scl_reg_rect)
        cv2.imwrite(f'test/station-services/out/stn_svc_layout.png', image)

        ocr_data, ocr_textlist = self.ocr.image_ocr(image)
        for res in ocr_data:
            for line in res:
                if "COMMODITIES" in line[1][0]:
                    loc = line[0]
                    tl_x, tl_y = loc[0]  # top left
                    tr = loc[1]
                    br = loc[2]
                    bl = loc[3]

                    # Check if button is in the middle column (right of mission board)
                    if tl_x > 600:
                        self.commodities_in_right = True
                    elif tl_x > 300:
                        self.commodities_in_center = True

                    # Check if button is in the bottom half (below mission board)
                    if tl_y > 200:
                        self.commodities_at_bottom = True

                    return True

        return False

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

        # Store image
        image = self.screen.get_screen_full()
        cv2.imwrite(f'test/station-services/select-mission.png', image)

        return True

    def goto_commodities_market(self) -> bool:
        """ Go to the Mission Board. Shows COMMUNITY GOALS, MISSION BOARD and PASSENGER LOUNGE. """
        # Go down to station services
        res = self.goto_station_services()
        if not res:
            return False

        # Try to determine commodities button on the services screen. Have seen it below Mission Board and too
        # right of the mission board.
        res = self.determine_commodities_location()
        if not res:
            logger.warning("Unable to find COMMODITIES MARKET button on Station Services screen.")
            return False

        self.vce.say("Connecting to commodities market, commander. ")

        # Select Mission Board
        self.keys.send("UI_Up")  # Is up needed?
        self.keys.send("UI_Left", hold=2)

        if self.commodities_at_bottom:
            self.keys.send("UI_Down")  # Commodities Market

        if self.commodities_in_center:
            self.keys.send("UI_Right")  # Commodities Market

        if self.commodities_in_right:
            self.keys.send("UI_Right")  # Commodities Market
            self.keys.send("UI_Right")  # Commodities Market

        self.keys.send("UI_Select")  # Commodities Market

        # Scale the regions based on the target resolution.
        scl_reg_rect = reg_scale_for_station(self.reg['commodities_market'], self.screen.screen_width, self.screen.screen_height)

        # Wait for screen to appear
        res = self.ocr.wait_for_text(["COMMODITIES"], scl_reg_rect)

        # Store image
        image = self.screen.get_screen_full()
        cv2.imwrite(f'test/commodities-market/commodities_market.png', image)

        if not res:
            return False

        # Load Market.json data for the market
        res = self.commodities_market.get_market_data()
        return res

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
        self.keys.send("UI_Select")
        sleep(1)  # give time to bring up menu

        # Store image
        image = self.screen.get_screen_full()
        cv2.imwrite(f'test/passenger-lounge/passenger_lounge.png', image)

        return True


class PassengerLounge:
    def __init__(self, station_services_in_ship: EDStationServicesInShip, ocr, keys, screen):
        self.parent = station_services_in_ship
        self.ocr = ocr
        self.keys = keys
        self.screen = screen

        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        # Nav Panel region covers the entire navigation panel.
        self.reg = {'no_cmpl_missions': {'rect': [0.47, 0.77, 0.675, 0.85]},
                    'mission_dest_col': {'rect': [0.47, 0.41, 0.64, 0.85]},
                    'complete_mission_col': {'rect': [0.47, 0.22, 0.675, 0.85]}}

        self.no_cmpl_missions_row_width = 384  # Buy/sell item width in pixels at 1920x1080
        self.no_cmpl_missions_row_height = 70  # Buy/sell item height in pixels at 1920x1080
        self.mission_dest_row_width = 326  # Buy/sell item width in pixels at 1920x1080
        self.mission_dest_row_height = 70  # Buy/sell item height in pixels at 1920x1080
        self.complete_mission_row_width = 384  # Buy/sell item width in pixels at 1920x1080
        self.complete_mission_row_height = 70  # Buy/sell item height in pixels at 1920x1080

    def goto_personal_transport_missions(self) -> bool:
        """ Go to the passenger lounge menu. """
        res = self.parent.goto_passenger_lounge()
        if not res:
            return False

        # Select Personal Transportation
        self.keys.send("UI_Up", repeat=3)
        self.keys.send("UI_Down", repeat=2)
        self.keys.send("UI_Select")  # select Personal Transport

        # Scale the regions based on the target resolution.
        scl_reg_rect = reg_scale_for_station(self.reg['mission_dest_col'], self.screen.screen_width, self.screen.screen_height)

        # Wait for screen to appear
        res = self.ocr.wait_for_text(["DESTINATION", "LOCKED"], scl_reg_rect)

        # Store image
        image = self.screen.get_screen_full()
        cv2.imwrite(f'test/passenger-lounge/personal_transport_missions.png', image)

        return res

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
        # Scale the regions based on the target resolution.
        scl_reg_rect = reg_scale_for_station(self.reg['complete_mission_col'], self.screen.screen_width, self.screen.screen_height)
        scl_row_w, scl_row_h = size_scale_for_station(self.complete_mission_row_width, self.complete_mission_row_height, self.screen.screen_width, self.screen.screen_height)

        return self.ocr.select_item_in_list("COMPLETE MISSION", scl_reg_rect, self.keys, scl_row_w, scl_row_h)

    def missions_ready_to_complete(self) -> bool:
        """ Check if the COMPLETE MISSIONS button is enabled (we have missions to turn in).
        True if there are missions, else False. """
        # Scale the regions based on the target resolution.
        scl_reg_rect = reg_scale_for_station(self.reg['no_cmpl_missions'], self.screen.screen_width, self.screen.screen_height)
        scl_row_w, scl_row_h = size_scale_for_station(self.no_cmpl_missions_row_width, self.no_cmpl_missions_row_height,
                                                      self.screen.screen_width, self.screen.screen_height)

        return self.ocr.is_text_in_region("COMPLETE MISSIONS", scl_reg_rect)

    def select_mission_with_dest(self, dest) -> bool:
        """ Select a mission with the required destination.
        True if there are missions, else False. """
        # Scale the regions based on the target resolution.
        scl_reg_rect = reg_scale_for_station(self.reg['mission_dest_col'], self.screen.screen_width, self.screen.screen_height)
        scl_row_w, scl_row_h = size_scale_for_station(self.mission_dest_row_width, self.mission_dest_row_height, self.screen.screen_width, self.screen.screen_height)

        return self.ocr.select_item_in_list(dest, scl_reg_rect, self.keys, scl_row_w, scl_row_h)


class CommoditiesMarket:
    def __init__(self, station_services_in_ship: EDStationServicesInShip, ocr, keys, screen):
        self.parent = station_services_in_ship
        self.ocr = ocr
        self.keys = keys
        self.screen = screen

        self.market_parser = MarketParser()
        # The reg rect is top left x, y, and bottom right x, y in fraction of screen resolution at 1920x1080
        self.reg = {'cargo_col': {'rect': [0.13, 0.227, 0.19, 0.90]},
                     'commodity_name_col': {'rect': [0.19, 0.227, 0.41, 0.90]},
                     'supply_demand_col': {'rect': [0.42, 0.227, 0.49, 0.90]}}
        self.commodity_row_width = 422  # Buy/sell item width in pixels at 1920x1080
        self.commodity_row_height = 35  # Buy/sell item height in pixels at 1920x1080

    def get_market_data(self) -> bool:
        """ Check to see if market data is updated (recent modified time) before loading it.
         Timeout if file modified time is unchanged
         @return: True if file modified time changed and new data loaded. False if file did not change.
         """
        start_time = time.time()
        while 1:
            # Check if market file modified within 15 secs
            if self.__get_time_since_market_mod() < 15:
                # read file
                self.market_parser.get_market_data()
                return True

            # Wait up to 15 secs before failing
            if time.time() - start_time > 15:
                return False

            sleep(1)

    def __get_time_since_market_mod(self) -> float:
        return time.time() - self.market_parser.get_file_modified_time()

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

    def buy_commodity(self, name: str, qty: int) -> bool:
        """ Buy qty of commodity. If qty >= 9999 then buy as much as possible.
        Assumed to be in the commodities screen. """
        # Determine if station sells the commodity!
        self.market_parser.get_market_data()
        if not self.market_parser.can_buy_item(name):
            self.parent.vce.say(f"Item '{name}' is not sold or has no stock at {self.market_parser.get_market_name()}.")
            logger.debug(f"Item '{name}' is not sold or has no stock at {self.market_parser.get_market_name()}.")
            return False

        self.select_buy()
        self.keys.send("UI_Right")
        self.keys.send("UI_Up", hold=2)

        self.parent.vce.say(f"Locating {name} to buy.")

        # Scale the regions based on the target resolution.
        scl_reg_rect = reg_scale_for_station(self.reg['commodity_name_col'], self.screen.screen_width, self.screen.screen_height)
        scl_row_w, scl_row_h = size_scale_for_station(self.commodity_row_width, self.commodity_row_height, self.screen.screen_width, self.screen.screen_height)

        found = self.ocr.select_item_in_list(name, scl_reg_rect, self.keys, scl_row_w, scl_row_h)
        if not found:
            return False

        if qty != 9999:
            self.parent.vce.say(f"Buying {qty} units of {name}, commander.")
        else:
            self.parent.vce.say(f"Buying all we can of {name}, commander.")

        self.keys.send("UI_Select")
        sleep(0.2) # Wait for popup
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
        return True

    def sell_commodity(self, name: str, qty: int) -> bool:
        """ Sell qty of commodity. If qty >= 9999 then sell as much as possible.
        Assumed to be in the commodities screen. """
        # Determine if station buys the commodity!
        self.market_parser.get_market_data()
        if not self.market_parser.can_sell_item(name):
            self.parent.vce.say(f"Item '{name}' is not bought at {self.market_parser.get_market_name()}.")
            logger.debug(f"Item '{name}' is not bought at {self.market_parser.get_market_name()}.")
            return False

        self.select_sell()
        self.keys.send("UI_Right")
        self.keys.send("UI_Up", hold=2)

        self.parent.vce.say(f"Locating {name} to sell.")

        # Scale the regions based on the target resolution.
        scl_reg_rect = reg_scale_for_station(self.reg['commodity_name_col'], self.screen.screen_width, self.screen.screen_height)
        scl_row_w, scl_row_h = size_scale_for_station(self.commodity_row_width, self.commodity_row_height, self.screen.screen_width, self.screen.screen_height)

        found = self.ocr.select_item_in_list(name, scl_reg_rect, self.keys, scl_row_w, scl_row_h)
        if not found:
            return False

        if qty != 9999:
            self.parent.vce.say(f"Selling {qty} units of {name}, commander.")
        else:
            self.parent.vce.say(f"Selling all our {name}, commander.")

        self.keys.send("UI_Select")
        sleep(0.5) # Wait for popup
        #self.keys.send("UI_Left")
        self.keys.send("UI_Up", repeat=2)

        # Increment count
        if qty != 9999:
            # TODO - need to determine how to reduce count to what is required to sell.
            self.keys.send("UI_Right", repeat=qty)

        self.keys.send("UI_Down")  # To Sell
        self.keys.send("UI_Select")  # Sell

        self.keys.send("UI_Back")
        return True

    def sell_all_commodities(self) -> bool:
        """ Sell all commodities.
        Assumed to be in the commodities screen. """

        # Get the current cargo from the cargo.json file
        cargo_parser = CargoParser()
        current_data = cargo_parser.current_data

        # Go through cargo and attempt to sell it all.
        for good in current_data["Inventory"]:
            self.sell_commodity(good['Name'], 9999)

        return True


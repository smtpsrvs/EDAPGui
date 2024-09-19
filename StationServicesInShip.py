from time import sleep
from OCR import OCR

"""
File:StationServicesInShip.py    

Description:
  TBD 

Author: Stumpii
"""


class StationServicesInShip:
    def __init__(self, screen, keys, voice):
        self.commodities_at_bottom = False
        self.commodities_in_middle = False
        self.screen = screen
        self.ocr = OCR(screen)
        self.keys = keys
        self.vce = voice
        self.passenger_lounge = PassengerLounge(self, self.ocr, self.keys)
        self.commodities_market = CommoditiesMarket(self, self.ocr, self.keys)
        self.region_connected_to = {'rect': [0.0, 0.0, 0.25, 0.25]}  # top left x, y, and bottom right x, y
        self.region_stn_svc_layout = {'rect': [0.05, 0.40, 0.60, 0.75]}  # top left x, y, and bottom right x, y
        self.region_commodities_market = {'rect': [0.0, 0.0, 0.25, 0.25]}  # top left x, y, and bottom right x, y

    def goto_station_services(self) -> bool:
        """ Goto Station Services. """
        # Go down to station services and select
        self.keys.send("UI_Back", repeat=5)  # make sure back in ship view
        self.keys.send("UI_Up", repeat=3)  # go to very top (refuel)
        # self.keys.send("UI_Left", hold=1)  # go to very left (refuel)

        self.keys.send("UI_Down")  # station services
        self.keys.send("UI_Select")  # station services

        # Wait for screen to appear
        res = self.ocr.wait_for_text("CONNECTED TO", self.region_connected_to,'region_connected_to')
        return res

    def determine_commodities_location(self):
        # Get the services layout as the layout may be different per station
        # There is probably a better way to do this!
        self.commodities_in_middle = False
        self.commodities_at_bottom = False

        image = self.ocr.capture_region(self.region_stn_svc_layout, 'region_stn_svc_layout')
        ocr_data, ocr_textlist = self.ocr.image_ocr(image)
        for res in ocr_data:
            for line in res:
                if "COMMODITIES MARKET" in line[1][0]:
                    loc = line[0]
                    tl_x, tl_y = loc[0]  # top left
                    tr = loc[1]
                    br = loc[2]
                    bl = loc[3]

                    # Check if button is in the middle column (right of mission board)
                    if tl_x > 300:
                        self.commodities_in_middle = True

                    # Check if button is in the bottom half (below mission board)
                    if tl_y > 200:
                        self.commodities_at_bottom = True

                    break

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

        # Try to determine commodities button on the services screen. Have seen it below Mission Board and too
        # right of the mission board.
        self.determine_commodities_location()

        self.vce.say("Connecting to commodities market, commander. ")

        # Select Mission Board
        self.keys.send("UI_Up")  # Is up needed?
        self.keys.send("UI_Left", hold=2)

        if self.commodities_at_bottom:
            self.keys.send("UI_Down")  # Commodities Market

        if self.commodities_in_middle:
            self.keys.send("UI_Right")  # Commodities Market

        self.keys.send("UI_Select")  # Commodities Market

        # Wait for screen to appear
        res = self.ocr.wait_for_text("CONNECTED TO", self.region_commodities_market, 'region_commodities_market')
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
        return True


class PassengerLounge:
    def __init__(self, station_services_in_ship: StationServicesInShip, ocr, keys):
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
        self.keys.send("UI_Down", repeat=2)
        self.keys.send("UI_Select")  # select Personal Transport

        # Wait for screen to appear
        res = self.ocr.wait_for_text("DESTINATION", self.reg['mission_dest_col'],'mission_dest_col')
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
        return self.ocr.select_item_in_list("COMPLETE MISSION", self.reg['complete_mission_col'],
                                            self.keys, 'complete_mission_col')

    def missions_ready_to_complete(self) -> bool:
        """ Check if the COMPLETE MISSIONS button is enabled (we have missions to turn in.
        True if there are missions, else False. """
        return self.ocr.is_text_in_region("COMPLETE MISSIONS", self.reg['missions'])

    def select_mission_with_dest(self, dest) -> bool:
        """ Select a mission with the required destination.
        True if there are missions, else False. """
        return self.ocr.select_item_in_list(dest, self.reg['mission_dest_col'], self.keys, 'mission_dest_col')


class CommoditiesMarket:
    def __init__(self, station_services_in_ship: StationServicesInShip, ocr, keys):
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

    def buy_commodity(self, name: str, qty: int) -> bool:
        """ Buy qty of commodity. If qty >= 9999 then buy as much as possible.
        Assumed to be in the commodities screen. """
        self.select_buy()
        self.keys.send("UI_Right")
        self.keys.send("UI_Up", hold=2)

        self.parent.vce.say(f"Locating {name} to buy.")
        found = self.ocr.select_item_in_list(name, self.reg['commodity_name_col'], self.keys, 'commodity_name_col')
        if not found:
            return False

        self.parent.vce.say(f"Buying {qty} units of {name}, commander.")

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

    def sell_commodity(self, name: str, qty: int) -> bool:
        """ Sell qty of commodity. If qty >= 9999 then sell as much as possible.
        Assumed to be in the commodities screen. """
        self.select_sell()
        self.keys.send("UI_Right")
        self.keys.send("UI_Up", hold=2)

        self.parent.vce.say(f"Locating {name} to sell.")
        found = self.ocr.select_item_in_list(name, self.reg['commodity_name_col'], self.keys, 'commodity_name_col')
        if not found:
            return False

        self.parent.vce.say(f"Selling {qty} units of {name}, commander.")

        self.keys.send("UI_Select")
        sleep(0.5) # Wait for popup
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


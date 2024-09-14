from time import sleep

import cv2

from EDlogger import logger
from OCR import OCR, crop_image_by_pct

"""
File:StationServicesInShip.py    

Description:
  TBD 

Author: Stumpii
"""


class StationServicesInShip:
    def __init__(self, screen, keys):
        self.screen = screen
        self.ocr = OCR()
        self.keys = keys
        self.passenger_lounge = PassengerLounge(self, self.ocr, self.keys)

        self.using_screen = True  # True to use screen, false to use an image. Set screen_image to the image
        self.screen_image = None  # Screen image captured from screen, or loaded by user for testing.

    def __capture_station_services_on_screen(self):
        """ Just grab the screen based on the region name/rect.
        Returns an unfiltered image, squared (no perspective).
         """
        rect = self.reg['nav_panel']['rect']

        abs_rect = [int(rect[0] * self.screen.screen_width), int(rect[1] * self.screen.screen_height),
                    int(rect[2] * self.screen.screen_width), int(rect[3] * self.screen.screen_height)]
        image = self.screen.get_screen_region(abs_rect)
        self.screen_image = image

        return image

    def __capture_station_services_from_image(self):
        """ Just grab the image based on the region name/rect.
        Returns an unfiltered image, squared (no perspective).
         """
        rect = self.reg['nav_panel']['rect']

        if self.screen_image is None:
            return None

        image = self.screen_image

        # Existing size
        h, w, ch = image.shape

        # Crop to leave only the selected rectangle
        x0 = int(w * rect[0])
        y0 = int(h * rect[1])
        x1 = int(w * rect[2])
        y1 = int(h * rect[3])

        # Crop image
        cropped = image[y0:y1, x0:x1]

        return cropped

    def capture_station_services(self):
        """ Just grab the nav_panel image based on the region name/rect.
            Returns an unfiltered image, squared (no perspective).
            Capture may be from an image or the screen.
         """
        if self.using_screen:
            return self.__capture_station_services_on_screen()
        else:
            return self.__capture_station_services_from_image()

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

        self.keys.send("UI_Right")
        sleep(0.1)
        self.keys.send("UI_Select")  # select Mission Board
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
        self.reg['mission_dest'] = {'rect': [0.46, 0.38, 0.65, 0.86]}  # Fraction with ref to the screen/image

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
        sleep(15)  # wait 15 second for missions menu to show up
        return True

    def goto_complete_missions(self) -> bool:
        """ Go to the passenger lounge menu. """
        res = self.goto_passenger_lounge()
        if not res:
            return False

        # Go to Complete Mission
        self.keys.send("UI_Right", repeat=2)
        self.keys.send("UI_Select")
        return True

    def any_completed_missions(self) -> bool:
        """ Are there completed missions? If NO COMPLETED MISSIONS return False, else True.
        Checks if text exists in a region using OCR."""
        no_missions = ["NO COMPLETED MISSIONS", "NOCOMPLETED MISSIONS"]

        img = self.capture_no_missions()

        ocr_textlist = self.ocr.image_simple_ocr(img)
        # print(str(ocr_textlist))

        if ocr_textlist is None:
            logger.debug("OCR data is [None] in Passenger Lounge screen.")
            return False

        for name in no_missions:
            if name in str(ocr_textlist):
                logger.debug("Found 'NO COMPLETED MISSIONS' text in Passenger Lounge screen.")
                return False

        logger.debug("Did not find 'NO COMPLETED MISSIONS' text in Passenger Lounge screen.")
        return True

    def check_mission_destination(self, destination) -> bool:
        """ Does the mission destination include the text being checked for.
        Checks if text exists in a region using OCR."""

        img = self.capture_mission_dest()
        img_selected = self.ocr.get_selected_item_image(img, 25, 10)

        ocr_textlist = self.ocr.image_simple_ocr(img_selected)
        print(str(ocr_textlist))

        if destination in str(ocr_textlist):
            logger.debug(f"Found '{destination}' text in destination {str(ocr_textlist)}.")
            return True
        else:
            logger.debug(f"Did not find '{destination}' text in destination {str(ocr_textlist)}.")
            return False

    def capture_no_missions(self):
        """ Just grab the image based on the region name/rect.
        Returns an unfiltered image, squared (no perspective).
         """
        rect = self.reg['missions']['rect']

        if self.parent.using_screen:
            image = self.parent.screen.get_screen_region_pct(rect)
        else:
            if self.parent.screen_image is None:
                return None
            image = crop_image_by_pct(self.parent.screen_image, rect)

        #cv2.imwrite('test/no_missions.png', image)
        return image

    def capture_mission_dest(self):
        """ Just grab the image based on the region name/rect.
        Returns an unfiltered image, squared (no perspective).
         """
        rect = self.reg['mission_dest']['rect']

        if self.parent.using_screen:
            image = self.parent.screen.get_screen_region_pct(rect)
        else:
            if self.parent.screen_image is None:
                return None
            image = crop_image_by_pct(self.parent.screen_image, rect)

        return image

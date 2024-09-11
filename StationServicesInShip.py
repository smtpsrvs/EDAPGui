from time import sleep

import numpy as np
import cv2
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
        self.ocr = OCR()
        self.keys = keys

        self.using_screen = True  # True to use screen, false to use an image. Set screen_image to the image
        self.screen_image = None  # Screen image captured from screen, or loaded by user for testing.

        self.reg = {}
        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        # Nav Panel region covers the entire navigation panel.
        self.reg['nav_panel'] = {'rect': [0.10, 0.23, 0.72, 0.83]} # Fraction with ref to the screen/image
        self.reg['tab_bar'] = {'rect': [0.0, 0.0, 1.0, 0.1152]} # Fraction with ref to the Nav Panel
        self.reg['location_panel'] = {'rect': [0.2218, 0.3069, 0.8537, 0.9652]} # Fraction with ref to the Nav Panel

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







    def hide_station_services(self):
        """ Hides the Nav Panel if open.
        """
        # Is nav panel active?
        active, active_tab_name = self.is_nav_panel_active()
        if active is not None:
            self.keys.send("UI_Back", repeat=10)
            self.keys.send("HeadLookReset")




from time import sleep

import numpy as np
import cv2

from EDlogger import logger
from OCR import OCR, crop_image_by_pct

"""
File:navPanel.py    

Description:
  TBD 

Author: Stumpii
"""



class NavPanel:
    def __init__(self, screen, keys):
        self.screen = screen
        self.ocr = OCR(screen)
        self.keys = keys

        self.using_screen = True  # True to use screen, false to use an image. Set screen_image to the image
        self.screen_image = None  # Screen image captured from screen, or loaded by user for testing.
        self.navigation_tab_text = "NAVIGATION"
        self.transactions_tab_text = "TRANSACTIONS"
        self.contacts_tab_text = "CONTACTS"
        self.target_tab_text = "TARGET"

        self.reg = {}
        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        # Nav Panel region covers the entire navigation panel.
        self.reg['nav_panel'] = {'rect': [0.10, 0.23, 0.72, 0.83]}  # Fraction with ref to the screen/image
        self.reg['tab_bar'] = {'rect': [0.0, 0.0, 1.0, 0.1152]}  # Fraction with ref to the Nav Panel
        self.reg['location_panel'] = {'rect': [0.2218, 0.3069, 0.8537, 0.9652]}  # Fraction with ref to the Nav Panel

    def capture_region_straightened(self, region):
        """ Grab the image based on the region name/rect.
        Returns an unfiltered image, either from screenshot or provided image.
         """
        rect = self.reg[region]['rect']

        if self.using_screen:
            image = self.screen.get_screen_region_pct(rect)
        else:
            if self.screen_image is None:
                return None
            image = crop_image_by_pct(self.screen_image, rect)

        # Straighten the image
        straightened = self.__nav_panel_perspective_warp(image)
        # cv2.imwrite(f'test/{region}.png', straightened)
        return straightened

    def __nav_panel_perspective_warp(self, image):
        """ Performs warping of the nav panel image and returns the result.
        The warping removes the perspective slanting of all sides so the
        returning image has vertical columns and horizontal rows for matching
        or OCR. """
        # Existing size
        h, w, ch = image.shape

        pts1 = np.float32(
            [[w * 0.05, h],  # bottom left
             [w, h * 0.835],  # bottom right
             [0, 0],  # top left
             [w * 0.99, 0]]  # top right
        )
        pts2 = np.float32(
            [[0, h],  # bottom left
             [w, h],  # bottom right
             [0, 0],  # top left
             [w, h * 0.0175]]  # top right
        )
        M = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(image, M, (w, h))

        return dst

    def capture_location_panel(self):
        """ Get the location panel from within the nav panel.
        Returns an image.
        """
        nav_panel = self.capture_region_straightened('nav_panel')

        # Existing size
        h, w, ch = nav_panel.shape

        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        location_panel_rect = self.reg['location_panel']['rect']

        # Crop to leave only the selected rectangle
        x0 = int(w * location_panel_rect[0])
        y0 = int(h * location_panel_rect[1])
        x1 = int(w * location_panel_rect[2])
        y1 = int(h * location_panel_rect[3])

        # Crop image
        location_panel = nav_panel[y0:y1, x0:x1]
        return location_panel

    def capture_tab_bar(self):
        """ Get the tab bar (NAVIGATION/TRANSACTIONS/CONTACTS/TARGET).
        Returns an image.
        """
        nav_pnl = self.capture_region_straightened('nav_panel')

        # Existing size
        h, w, ch = nav_pnl.shape

        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        tab_bar_rect = self.reg['tab_bar']['rect']

        # Crop to leave only the selected rectangle
        x0 = int(w * tab_bar_rect[0])
        y0 = int(h * tab_bar_rect[1])
        x1 = int(w * tab_bar_rect[2])
        y1 = int(h * tab_bar_rect[3])

        # Crop image
        tab_bar = nav_pnl[y0:y1, x0:x1]

        #cv2.imwrite('test/nav-panel/tab_bar.png', tab_bar)

        #cv2.imshow("tab_bar", tab_bar)

        return tab_bar

    def show_nav_panel(self):
        """ Shows the Nav Panel. Opens the Nav Panel if not already open.
        Returns True if successful, else False.
        """
        # Is nav panel active?
        active, active_tab_name = self.is_nav_panel_active()
        if active:
            return active, active_tab_name
        else:
            print("Open Nav Panel")
            self.keys.send("UI_Back", repeat=10)
            self.keys.send("HeadLookReset")
            self.keys.send('UIFocus', state=1)
            self.keys.send('UI_Left')
            self.keys.send('UIFocus', state=0)
            sleep(0.5)

            # Check if it opened
            active, active_tab_name = self.is_nav_panel_active()
            if active:
                return active, active_tab_name
            else:
                return False, ""

    def show_navigation_tab(self) -> bool:
        """ Shows the NAVIGATION tab of the Nav Panel. Opens the Nav Panel if not already open.
        Returns True if successful, else False.
        """
        # Show nav panel
        active, active_tab_name = self.show_nav_panel()
        if not active:
            print("Nav Panel could not be opened")
            return False
        elif active_tab_name is self.navigation_tab_text:
            # Do nothing
            return True
        elif active_tab_name is self.transactions_tab_text:
            # self.keys.send('CycleNextPanel', hold=0.2)
            # sleep(0.2)
            # self.keys.send('CycleNextPanel', hold=0.2)
            self.keys.send('CycleNextPanel', repeat=2)
            return True
        elif active_tab_name is self.contacts_tab_text:
            # self.keys.send('CycleNextPanel', hold=0.2)
            self.keys.send('CycleNextPanel')
            return True
        elif active_tab_name is self.target_tab_text:
            # self.keys.send('CycleNextPanel', hold=0.2)
            self.keys.send('CycleNextPanel')
            return True

    def show_contacts_tab(self) -> bool:
        """ Shows the CONTACTS tab of the Nav Panel. Opens the Nav Panel if not already open.
        Returns True if successful, else False.
        """
        # Show nav panel
        active, active_tab_name = self.show_nav_panel()
        if not active:
            print("Nav Panel could not be opened")
            return False
        elif active_tab_name is self.navigation_tab_text:
            # self.keys.send('CycleNextPanel', hold=0.2)
            # sleep(0.2)
            # self.keys.send('CycleNextPanel', hold=0.2)
            self.keys.send('CycleNextPanel', repeat=2)
            return True
        elif active_tab_name is self.transactions_tab_text:
            # self.keys.send('CycleNextPanel', hold=0.2)
            self.keys.send('CycleNextPanel')
            return True
        elif active_tab_name is self.contacts_tab_text:
            # Do nothing
            return True
        elif active_tab_name is self.target_tab_text:
            # self.keys.send('CycleNextPanel', hold=0.2)
            # sleep(0.2)
            # self.keys.send('CycleNextPanel', hold=0.2)
            self.keys.send('CycleNextPanel', repeat=2)
            return True

    def hide_nav_panel(self):
        """ Hides the Nav Panel if open.
        """
        # Is nav panel active?
        active, active_tab_name = self.is_nav_panel_active()
        if active is not None:
            self.keys.send("UI_Back", repeat=10)
            self.keys.send("HeadLookReset")

    def is_nav_panel_active(self) -> (bool, str):
        """ Determine if the Nav Panel is open and if so, which tab is active.
            Returns True if active, False if not and also the string of the tab name.
        """
        tab_bar = self.capture_tab_bar()
        img_selected, ocr_data, ocr_textlist = self.ocr.get_highlighted_item_data(tab_bar, 50, 10)
        if img_selected is not None:
            if self.navigation_tab_text in str(ocr_textlist):
                return True, self.navigation_tab_text
            if self.transactions_tab_text in str(ocr_textlist):
                return True, self.transactions_tab_text
            if self.contacts_tab_text in str(ocr_textlist):
                return True, self.contacts_tab_text
            if self.target_tab_text in str(ocr_textlist):
                return True, self.target_tab_text

        return False, ""

    def lock_destination(self, dst_name) -> bool:
        """ Opens Nav Panel, Navigation Tab, scrolls locations and if the requested
        location is found, lock onto destination. Close Nav Panel.
        """
        res = self.show_navigation_tab()
        if not res:
            print("Nav Panel could not be opened")
            return False

        self.keys.send("UI_Down")  # go down
        self.keys.send("UI_Up", hold=2)  # got to top row

        found = self.find_destination_in_list(dst_name)
        if found:
            self.keys.send("UI_Select", repeat=2)  # Select it and lock target

        self.hide_nav_panel()
        return found

    def find_destination_in_list(self, dst_name) -> bool:
        # tries is the number of rows to go through to find the item looking for
        # the Nav Panel should be filtered to reduce the number of rows in the list
        tries = 0
        in_list = False  # Have we seen one item yet? Prevents quiting if we have not selected the first item.
        while tries < 50:
            # Get the location panel image
            loc_panel = self.capture_location_panel()

            # Find the selected item/menu (solid orange)
            img_selected = self.ocr.get_highlighted_item_in_image(loc_panel, 100, 10)
            # Check if end of list.
            if img_selected is None and in_list:
                logger.debug(f"Did not find '{dst_name}' in list.")
                return False

            # OCR the selected item
            ocr_textlist = self.ocr.image_simple_ocr(img_selected)
            if ocr_textlist is not None:
                if dst_name in str(ocr_textlist):
                    logger.debug(f"Found '{dst_name}' in list.")
                    return True
                else:
                    in_list = True
                    tries += 1
                    self.keys.send("UI_Down")  # up to next item

        logger.debug(f"Did not find '{dst_name}' in list.")
        return False

    def request_docking(self) -> bool:
        """ Try to request docking.
        """
        res = self.show_contacts_tab()
        if not res:
            print("Contacts Panel could not be opened")
            return False

        # On the CONTACT TAB, go to top selection, do this 4 seconds to ensure at top
        # then go right, which will be "REQUEST DOCKING" and select it
        self.keys.send('UI_Up', hold=4)
        self.keys.send('UI_Right')
        self.keys.send('UI_Select')
        sleep(0.3)

        self.hide_nav_panel()
        return True

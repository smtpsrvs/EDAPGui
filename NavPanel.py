from __future__ import annotations

from time import sleep
import numpy as np
import cv2
from EDAP_data import *
from EDKeys import EDKeys
from EDlogger import logger
from OCR import OCR
from Screen import Screen
from StatusParser import StatusParser
from Test_Routines import reg_scale_for_station, size_scale_for_station
from strsimpy.jaro_winkler import JaroWinkler

"""
File:navPanel.py    

Description:
  TBD 

Author: Stumpii
"""


class NavPanel:
    def __init__(self, screen, keys, cb):
        self.screen = screen
        self.ocr = OCR(screen)
        self.keys = keys
        self.status_parser = StatusParser()
        self.ap_ckb = cb

        self.navigation_tab_text = "NAVIGATION"
        self.transactions_tab_text = "TRANSACTIONS"
        self.contacts_tab_text = "CONTACTS"
        self.target_tab_text = "TARGET"
        self.nav_pnl_coords = None  # [top left, top right, bottom left, bottom right]

        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        # Nav Panel region covers the entire navigation panel.
        self.reg = {'nav_panel': {'rect': [0.11, 0.21, 0.70, 0.86]}}
        self.sub_reg = {'tab_bar': {'rect': [0.0, 0.0, 1.0, 0.08]},
                        'location_panel': {'rect': [0.2218, 0.3, 0.8, 1.0]}}
        self.nav_pnl_tab_width = 260  # Nav panel tab width in pixels at 1920x1080
        self.nav_pnl_tab_height = 35  # Nav panel tab height in pixels at 1920x1080
        self.nav_pnl_location_width = 500  # Nav panel location width in pixels at 1920x1080
        self.nav_pnl_location_height = 35  # Nav panel location height in pixels at 1920x1080

    def capture_region_straightened(self, region):
        """ Grab the image based on the region name/rect.
        Returns an unfiltered image, either from screenshot or provided image.
        @param region: The region to check in % (0.0 - 1.0).
        """
        rect = region['rect']
        image = self.screen.get_screen_region_pct(rect)
        if image is None:
            return None

        cv2.imwrite(f'test/nav-panel/out/nav_panel_original.png', image)

        # Straighten the image
        straightened = self.__nav_panel_perspective_warp(image)

        cv2.imwrite(f'test/nav-panel/out/nav_panel_straight.png', straightened)
        return straightened

    def capture_nav_panel_straightened(self):
        """ Grab the image based on the panel coordinates.
        Returns an unfiltered image, either from screenshot or provided image, or None if an image cannot
        be grabbed.
        """
        if self.nav_pnl_coords is None:
            logger.warning(f"Nav Panel Calibration has not been performed. Cannot continue.")
            self.ap_ckb('log', 'Nav Panel Calibration has not been performed. Cannot continue.')
            return None

        full_image = self.screen.get_screen_full()

        # Get the nav panel co-ordinates
        [x0, y0] = self.nav_pnl_coords[0]  # top left
        [x1, y1] = self.nav_pnl_coords[1]  # top right
        [x2, y2] = self.nav_pnl_coords[2]  # bottom left
        [x3, y3] = self.nav_pnl_coords[3]  # bottom right

        # Calculate the bounding rectangle
        left = min(x0, x2)
        top = min(y0, y1)
        right = max(x1, x3)
        bottom = max(y2, y3)

        # Calculate the co-ordinates with reference to the bounding rectangle
        [xn0, yn0] = [x0 - left, y0 - top]
        [xn1, yn1] = [x1 - left, y1 - top]
        [xn2, yn2] = [x2 - left, y2 - top]
        [xn3, yn3] = [x3 - left, y3 - top]

        new_coords = [[xn0, yn0], [xn1, yn1], [xn2, yn2], [xn3, yn3]]

        # Crop the screen to the rectangle containing the nav panel
        image = self.screen.crop_image(full_image, [left, top, right, bottom])
        cv2.imwrite(f'test/nav-panel/out/nav_panel_original.png', image)

        # Straighten the image
        straightened = self.__nav_panel_perspective_warp_full(image, new_coords)
        cv2.imwrite(f'test/nav-panel/out/nav_panel_straight.png', straightened)

        return straightened

    def __nav_panel_perspective_warp_full(self, image, coords):
        """ Performs warping of the nav panel image and returns the result.
        The warping removes the perspective slanting of all sides so the
        returning image has vertical columns and horizontal rows for matching
        or OCR. """
        # Existing size
        h, w, ch = image.shape

        pts1 = np.float32(
            [coords[2],  # bottom left
             coords[3],  # bottom right
             coords[0],  # top left
             coords[1]]  # top right
        )
        pts2 = np.float32(
            [[0, h],  # bottom left
             [w, h],  # bottom right
             [0, 0],  # top left
             [w, 0]]  # top right
        )
        M = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(image, M, (w, h))

        return dst

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
        Returns an image, or None.
        """
        # Scale the regions based on the target resolution.
        # scl_reg_rect = reg_scale_for_station(self.reg['nav_panel'], self.screen.screen_width, self.screen.screen_height)

        #nav_panel = self.capture_region_straightened(scl_reg_rect)
        nav_panel = self.capture_nav_panel_straightened()
        if nav_panel is None:
            return None

        # Existing size
        h, w, ch = nav_panel.shape

        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        location_panel_rect = self.sub_reg['location_panel']['rect']

        # Crop to leave only the selected rectangle
        x0 = int(w * location_panel_rect[0])
        y0 = int(h * location_panel_rect[1])
        x1 = int(w * location_panel_rect[2])
        y1 = int(h * location_panel_rect[3])

        # Crop image
        location_panel = nav_panel[y0:y1, x0:x1]
        cv2.imwrite(f'test/nav-panel/out/nav_panel_location_panel.png', location_panel)
        return location_panel

    def capture_tab_bar(self):
        """ Get the tab bar (NAVIGATION/TRANSACTIONS/CONTACTS/TARGET).
        Returns an image, or None.
        """
        # Scale the regions based on the target resolution.
        #scl_reg_rect = reg_scale_for_station(self.reg['nav_panel'], self.screen.screen_width, self.screen.screen_height)

        #nav_pnl_st = self.capture_region_straightened(scl_reg_rect)
        nav_pnl_st = self.capture_nav_panel_straightened()
        if nav_pnl_st is None:
            return None

        # Existing size
        h, w, ch = nav_pnl_st.shape

        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        tab_bar_rect = self.sub_reg['tab_bar']['rect']

        # Crop to leave only the selected rectangle
        x0 = int(w * tab_bar_rect[0])
        y0 = int(h * tab_bar_rect[1])
        x1 = int(w * tab_bar_rect[2])
        y1 = int(h * tab_bar_rect[3])

        # Crop image
        tab_bar = nav_pnl_st[y0:y1, x0:x1]
        cv2.imwrite('test/nav-panel/out/tab_bar.png', tab_bar)

        return tab_bar

    def show_nav_panel(self):
        """ Shows the Nav Panel. Opens the Nav Panel if not already open.
        Returns True if successful, else False.
        """
        # Is nav panel active?
        active, active_tab_name = self.is_nav_panel_active()
        if active:
            # Store image
            image = self.screen.get_screen_full()
            cv2.imwrite(f'test/nav-panel/nav_panel_full.png', image)
            return active, active_tab_name
        else:
            print("Open Nav Panel")
            self.goto_ship_view()
            self.keys.send("HeadLookReset")

            self.keys.send('UIFocus', state=1)
            self.keys.send('UI_Left')
            self.keys.send('UIFocus', state=0)
            sleep(0.5)

            # Check if it opened
            active, active_tab_name = self.is_nav_panel_active()
            if active:
                # Store image
                image = self.screen.get_screen_full()
                cv2.imwrite(f'test/nav-panel/nav_panel_full.png', image)
                return active, active_tab_name
            else:
                return False, ""

    def goto_ship_view(self):
        # TODO - does this work in all cases?
        # TODO - move this to a better place
        # TODO - Use GET_GUI_FOCUS instead
        status = self.status_parser.get_cleaned_data()
        if status['GuiFocus'] == GuiFocusNoFocus:
            return True  # Do nothing
        elif status['GuiFocus'] == GuiFocusInternalPanel:
            self.keys.send("UI_Back")
        elif status['GuiFocus'] == GuiFocusExternalPanel:
            self.keys.send("UI_Back")
        elif status['GuiFocus'] == GuiFocusCommsPanel:
            self.keys.send("UI_Back")
        elif status['GuiFocus'] == GuiFocusRolePanel:
            self.keys.send("UI_Back")
        elif status['GuiFocus'] == GuiFocusStationServices:
            self.keys.send("UI_Back")
        elif status['GuiFocus'] == GuiFocusGalaxyMap:
            self.keys.send("UI_Back")
        elif status['GuiFocus'] == GuiFocusSystemMap:
            self.keys.send("UI_Back")
            self.keys.send("UI_Back")  # In case in system map from galaxy map
        elif status['GuiFocus'] == GuiFocusOrrery:
            self.keys.send("UI_Back")
            self.keys.send("UI_Back")  # In case in system map from galaxy map
        elif status['GuiFocus'] == GuiFocusFSS:
            self.keys.send("UI_Back")
        elif status['GuiFocus'] == GuiFocusSAA:
            self.keys.send("UI_Back")
        elif status['GuiFocus'] == GuiFocusCodex:
            self.keys.send("UI_Back")

    def show_navigation_tab(self) -> bool | None:
        """ Shows the NAVIGATION tab of the Nav Panel. Opens the Nav Panel if not already open.
        Returns True if successful, else False.
        """
        # Show nav panel
        active, active_tab_name = self.show_nav_panel()
        if active is None:
            return None
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
            self.keys.send('CycleNextPanel', repeat=3)
            return True
        elif active_tab_name is self.contacts_tab_text:
            # self.keys.send('CycleNextPanel', hold=0.2)
            self.keys.send('CycleNextPanel', repeat=2)
            return True
        elif active_tab_name is self.target_tab_text:
            # self.keys.send('CycleNextPanel', hold=0.2)
            self.keys.send('CycleNextPanel', repeat=2)
            return True

    def show_contacts_tab(self) -> bool | None:
        """ Shows the CONTACTS tab of the Nav Panel. Opens the Nav Panel if not already open.
        Returns True if successful, else False.
        """
        # Show nav panel
        active, active_tab_name = self.show_nav_panel()
        if active is None:
            return None
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
            self.keys.send('CycleNextPanel', repeat=3)
            return True

    def hide_nav_panel(self):
        """ Hides the Nav Panel if open.
        """
        # active, active_tab_name = self.is_nav_panel_active()
        # if active is not None:

        # Is nav panel active?
        status = self.status_parser.get_cleaned_data()
        if status['GuiFocus'] == GuiFocusExternalPanel:
            self.keys.send("UI_Back")
            self.keys.send("HeadLookReset")

    def is_nav_panel_active(self) -> (bool, str):
        """ Determine if the Nav Panel is open and if so, which tab is active.
            Returns True if active, False if not and also the string of the tab name.
        """
        # Check if nav panel is open
        status = self.status_parser.get_cleaned_data()
        if status['GuiFocus'] != GuiFocusExternalPanel:
            return False, ""

        # Try this 'n' times before giving up
        for i in range(10):
            # Is open, so proceed
            tab_bar = self.capture_tab_bar()
            if tab_bar is None:
                return None

            # Determine the nav panel tab size at this resolution
            scl_row_w, scl_row_h = size_scale_for_station(self.nav_pnl_tab_width, self.nav_pnl_tab_height,
                                                          self.screen.screen_width, self.screen.screen_height)

            img_selected, ocr_data, ocr_textlist = self.ocr.get_highlighted_item_data(tab_bar, scl_row_w, scl_row_h)
            if img_selected is not None:
                if self.navigation_tab_text in str(ocr_textlist):
                    return True, self.navigation_tab_text
                if self.transactions_tab_text in str(ocr_textlist):
                    return True, self.transactions_tab_text
                if self.contacts_tab_text in str(ocr_textlist):
                    return True, self.contacts_tab_text
                if self.target_tab_text in str(ocr_textlist):
                    return True, self.target_tab_text

            # Wait and retry
            sleep(1)

        # Did not find anything
        return False, ""

    def lock_destination(self, dst_name) -> bool:
        """ Checks if destination is already locked and if not, Opens Nav Panel, Navigation Tab,
        scrolls locations and if the requested location is found, lock onto destination. Close Nav Panel.
        Returns True if the destination is already locked, or if it is successfully locked.
        """
        # Checks if the desired destination is already locked
        status = self.status_parser.get_cleaned_data()
        if status['Destination'] is not None:
            cur_dest = status['Destination']['Name']
            # print(f"wanted dest: {dst_name}. Current dest: {cur_dest}")
            if cur_dest.upper() == dst_name.upper():
                return True

        res = self.show_navigation_tab()
        if not res:
            print("Nav Panel could not be opened")
            return False

        found = self.find_destination_in_list(dst_name)
        if found:
            self.keys.send("UI_Select", repeat=2)  # Select it and lock target
        else:
            return False

        self.hide_nav_panel()
        return found

    def scroll_to_top_of_list(self) -> bool | None:
        """ Attempts to scroll to the top of the list by holding 'up' and waiting until the resulting OCR
        stops changing. This should be at the top of the list.
        """
        self.keys.send("UI_Down")  # go down in case we are at the top and don't want to go to the bottom
        self.keys.send("UI_Up", state=1)  # got to top row

        ocr_textlist_last = ""
        tries = 0
        in_list = False  # Have we seen one item yet? Prevents quiting if we have not selected the first item.
        while 1:
            # Get the location panel image
            loc_panel = self.capture_location_panel()
            if loc_panel is None:
                return None

            # Determine the nav panel tab size at this resolution
            scl_row_w, scl_row_h = size_scale_for_station(self.nav_pnl_location_width, self.nav_pnl_location_height,
                                                          self.screen.screen_width, self.screen.screen_height)

            # Find the selected item/menu (solid orange)
            img_selected, x, y = self.ocr.get_highlighted_item_in_image(loc_panel, scl_row_w, scl_row_h)

            # Check if end of list.
            if img_selected is None and in_list:
                #logger.debug(f"Off end of list. Did not find '{dst_name}' in list.")
                self.keys.send("UI_Up", state=0)  # got to top row
                return False

            # OCR the selected item
            ocr_textlist = self.ocr.image_simple_ocr(img_selected)
            if ocr_textlist is not None:
                # Check if list has not changed (we are at the top)
                if ocr_textlist == ocr_textlist_last:
                    tries = tries + 1
                else:
                    tries = 0
                    ocr_textlist_last = ocr_textlist

                # Require some counts in case we hit multiple 'UNIDENTIFIED SIGNAL SOURCE',
                # 'CONFLICT ZONE' or other repetitive text
                if tries >= 3:
                    self.keys.send("UI_Up", state=0)  # got to top row
                    return True

    def find_destination_in_list(self, dst_name) -> bool:
        # tries is the number of rows to go through to find the item looking for
        # the Nav Panel should be filtered to reduce the number of rows in the list

        # Scroll to top of list
        res = self.scroll_to_top_of_list()
        if not res:
            logger.debug(f"Unable to scroll to top of list.")
            return False

        # Class for text similarity metrics
        jarowinkler = JaroWinkler()

        y_last = -1
        in_list = False  # Have we seen one item yet? Prevents quiting if we have not selected the first item.
        while 1:
            # Get the location panel image
            loc_panel = self.capture_location_panel()
            if loc_panel is None:
                return False

            # Determine the nav panel tab size at this resolution
            scl_row_w, scl_row_h = size_scale_for_station(self.nav_pnl_location_width, self.nav_pnl_location_height,
                                                          self.screen.screen_width, self.screen.screen_height)

            # Find the selected item/menu (solid orange)
            img_selected, x, y = self.ocr.get_highlighted_item_in_image(loc_panel, scl_row_w, scl_row_h)
            # Check if end of list.
            if img_selected is None and in_list:
                logger.debug(f"Off end of list. Did not find '{dst_name}' in list.")
                return False

            # Check if this item is above the last item (we cycled to top).
            if y < y_last - 100:
                logger.debug(f"Cycled back to top. Did not find '{dst_name}' in list.")
                return False
            else:
                y_last = y

            # OCR the selected item
            sim_match = 0.9  # Similarity match 0.0 - 1.0 for 0% - 100%)
            ocr_textlist = self.ocr.image_simple_ocr(img_selected)
            if ocr_textlist is not None:
                sim = jarowinkler.similarity(f"['{dst_name.upper()}']", str(ocr_textlist))
                # print(f"Similarity of ['{dst_name.upper()}'] and {str(ocr_textlist)} is {sim}")
                if sim > sim_match:
                    logger.debug(f"Found '{dst_name}' in list.")
                    return True
                else:
                    in_list = True
                    self.keys.send("UI_Down")  # up to next item

    def request_docking(self) -> bool:
        """ Try to request docking.
        """
        res = self.show_contacts_tab()
        if res is None:
            return None
        if not res:
            print("Contacts Panel could not be opened")
            return False

        # On the CONTACT TAB, go to top selection, do this 4 seconds to ensure at top
        # then go right, which will be "REQUEST DOCKING" and select it
        self.keys.send("UI_Down")  # go down
        self.keys.send('UI_Up', hold=2)  # got to top row
        self.keys.send('UI_Right')
        self.keys.send('UI_Select')
        sleep(0.3)

        self.hide_nav_panel()
        return True


# Usage Example
if __name__ == "__main__":
    scr = Screen()
    mykeys = EDKeys()
    mykeys.activate_window = True  # Helps with single steps testing
    nav_pnl = NavPanel(scr, mykeys, None)
    nav_pnl.scroll_to_top_of_list()
    #nav_pnl.find_destination_in_list("ssss")

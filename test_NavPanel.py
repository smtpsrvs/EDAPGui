import logging
import os
import unittest
from tkinter import messagebox

import cv2
import numpy as np

from EDAP_data import FlagsDocked
from EDKeys import EDKeys
from EDlogger import logger
from EDNavigationPanel import EDNavigationPanel
from Screen import Screen
from StatusParser import StatusParser
from Test_Routines import draw_station_regions


def is_running() -> bool:
    scr = Screen()
    return scr.elite_window_exists()


def is_docked() -> bool:
    status = StatusParser()
    return status.get_flag(FlagsDocked)


class NavPanelTestCase(unittest.TestCase):
    running = is_running()
    docked = is_docked()

    def test_draw_regions_on_images(self):
        """
        Does NOT require Elite Dangerous to be running.
        ======================================================================
        """
        nav_pnl = EDNavigationPanel(None, None, None)
        draw_station_regions('test/nav-panel/', nav_pnl.reg)

        self.assertEqual(True, True)  # add assertion here

    def test_draw_regions_on_image(self):
        """
        Does NOT require Elite Dangerous to be running.
        ======================================================================
        """
        image_path = "test/nav-panel/Screenshot 1920x1080 2024-10-14 20-45-25.png"
        image_path = "test/nav-panel/Screenshot 1920x1200 2024-09-07 09-08-36.png"
        #image_path = "test/nav-panel/Screenshot_2024-09-09_195949.png"
        #image_path = "test/nav-panel/CBB63634-4208-49F6-A5DD-640E589D79B3.png"
        frame = cv2.imread(image_path)

        scr = Screen()
        scr.using_screen = False
        scr.set_screen_image(frame)
        nav_pnl = EDNavigationPanel(scr, None, None)

        # Scale the regions based on the target resolution.
        #scl_reg_rect = reg_scale_for_station(nav_pnl.reg['nav_panel'], scr.screen_width, scr.screen_height)

        #straightened = nav_pnl.capture_region_straightened(scl_reg_rect)
        straightened = nav_pnl.capture_nav_panel_straightened()
        self.assertIsNone(straightened, "Could not grab Nav Panel image.")  # add assertion here

        res = nav_pnl.capture_location_panel()
        self.assertIsNone(res, "Could not grab Nav Panel Location image.")  # add assertion here

        res = nav_pnl.capture_tab_bar()
        self.assertIsNone(res, "Could not grab Nav Panel Tab bar image.")  # add assertion here

        self.assertEqual(True, True)  # add assertion here

    @unittest.skipUnless(running, "Elite Dangerous is not running")
    def test_nav_panel_lock_station(self):
        logger.setLevel(logging.DEBUG)  # Default to log all debug when running this file.

        name = "Maybury Town"

        scr = Screen()
        keys = EDKeys()
        keys.activate_window = True  # Helps with single steps testing
        nav_pnl = EDNavigationPanel(scr, keys, None)

        res = nav_pnl.lock_destination(name)

        self.assertTrue(res, "Failed to lock destination.")  # add assertion here

    @unittest.skipUnless(running, "Elite Dangerous is not running")
    def test_nav_panel_request_docking(self):
        logger.setLevel(logging.DEBUG)  # Default to log all debug when running this file.

        scr = Screen()
        keys = EDKeys()
        keys.activate_window = True  # Helps with single steps testing
        nav_pnl = EDNavigationPanel(scr, keys, None)

        res = nav_pnl.request_docking_ocr()
        self.assertTrue(res, "Failed to request docking.")  # add assertion here


if __name__ == '__main__':
    unittest.main()

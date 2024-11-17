import unittest

import cv2

from EDKeys import EDKeys
from EDWayPoint import EDWayPoint
from Screen import Screen


def select_system(target_name) -> bool:
    """ Select a system in the galaxy map. """
    scr = Screen()
    keys = EDKeys()
    keys.activate_window = True  # Helps with single steps testing

    waypoint = EDWayPoint(True)
    return waypoint.set_waypoint_target_odyssey(scr, keys, target_name, None)


class GalaxyMapTestCase(unittest.TestCase):
    def test_draw_system_info(self):
        """
        Does NOT require Elite Dangerous to be running.
        ======================================================================
        """
        image_path = "test/test-images/Screenshot 2024-10-14 20-45-42.png"
        image_path = "test/test-images/Screenshot 2024-10-14 20-48-01.png"
        image_path = "test/test-images/Screenshot_0006 2024-11-16 17-56-19.png"
        system = "Beimech"

        frame = cv2.imread(image_path)

        scr = Screen()
        scr.using_screen = False
        scr.set_screen_image(frame)
        ed_wp = EDWayPoint(True)

        system_name = ed_wp.get_system_from_system_info_panel(scr, system)
        if system_name is None:
            self.assertTrue(False, f"Unable to find system info panel.")  # add assertion here

        res = system.upper() == system_name.upper()
        self.assertTrue(res, f"Unable to find system {system}")  # add assertion here

    def test_System1(self):
        """ A single system (no duplicates). """
        system = "ROBIGO"
        res = select_system(system)
        self.assertTrue(res, f"Unable to find system {system}")  # add assertion here

    def test_System2(self):
        """ A duplicate system with multiple similar named systems. """
        system = "LHS 54"
        res = select_system(system)
        self.assertTrue(res, f"Unable to find system {system}")  # add assertion here

    def test_System3(self):
        system = "Cubeo"
        res = select_system(system)
        self.assertTrue(res, f"Unable to find system {system}")  # add assertion here

    def test_AllSystems(self):
        self.test_System1()
        self.test_System2()
        self.test_System3()

        self.assertTrue(True, f"Unable to find systems")  # add assertion here


if __name__ == '__main__':
    unittest.main()

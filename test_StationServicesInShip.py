import unittest
from EDKeys import EDKeys
from Screen import Screen
from StationServicesInShip import StationServicesInShip
from Test_Routines import draw_regions
from Voice import Voice


def does_elite_window_exist() -> bool:
    scr = Screen()
    return scr.elite_window_exists()


class CommoditiesMarketTestCase(unittest.TestCase):
    elite_win_exists = does_elite_window_exist()

    def test_draw_regions_on_images(self):
        """
        Does NOT require Elite Dangerous to be running.
        ======================================================================
        """
        stn_svc = StationServicesInShip(None, None, None)
        draw_regions('test/commodities-market/', stn_svc.commodities_market.reg)

        self.assertEqual(True, True)  # add assertion here

    @unittest.skipUnless(elite_win_exists, "Elite Dangerous is not running")
    def test_buy_commodity(self):
        """
        DOES require Elite Dangerous to be running.
        ======================================================================
        """
        name = "gold"
        count = 4

        scr = Screen()
        keys = EDKeys()
        vce = Voice()
        vce.v_enabled = True
        keys.activate_window = True  # Helps with single steps testing
        stn_svc = StationServicesInShip(scr, keys, vce)

        stn_svc.goto_commodities_market()
        stn_svc.commodities_market.buy_commodity(name, count)

        self.assertEqual(True, True)  # add assertion here

    @unittest.skipUnless(elite_win_exists, "Elite Dangerous is not running")
    def test_sell_commodity(self):
        """
        DOES require Elite Dangerous to be running.
        ======================================================================
        """
        name = "gold"
        count = 4

        scr = Screen()
        keys = EDKeys()
        vce = Voice()
        vce.v_enabled = True
        keys.activate_window = True  # Helps with single steps testing
        stn_svc = StationServicesInShip(scr, keys, vce)

        stn_svc.goto_commodities_market()
        stn_svc.commodities_market.sell_commodity(name, count)

        self.assertEqual(True, True)  # add assertion here

    @unittest.skipUnless(elite_win_exists, "Elite Dangerous is not running")
    def test_sell_all_commodities(self):
        """
        DOES require Elite Dangerous to be running.
        ======================================================================
        """
        scr = Screen()
        keys = EDKeys()
        vce = Voice()
        vce.v_enabled = True
        keys.activate_window = True  # Helps with single steps testing
        stn_svc = StationServicesInShip(scr, keys, vce)

        stn_svc.goto_commodities_market()
        stn_svc.commodities_market.sell_all_commodities()

        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()

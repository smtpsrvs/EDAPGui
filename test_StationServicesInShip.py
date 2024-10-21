import logging
import unittest

from EDAP_data import FlagsDocked
from EDKeys import EDKeys
from EDlogger import logger
from Screen import Screen
from StationServicesInShip import StationServicesInShip
from StatusParser import StatusParser
from Test_Routines import draw_station_regions
from Voice import Voice


def is_running() -> bool:
    scr = Screen()
    return scr.elite_window_exists()


def is_docked() -> bool:
    status = StatusParser()
    return status.get_flag(FlagsDocked)


class CommoditiesMarketTestCase(unittest.TestCase):
    running = is_running()
    docked = is_docked()

    def test_draw_regions_on_images(self):
        """
        Does NOT require Elite Dangerous to be running.
        ======================================================================
        """
        stn_svc = StationServicesInShip(None, None, None)
        draw_station_regions('test/commodities-market/', stn_svc.commodities_market.reg)

        self.assertEqual(True, True)  # add assertion here

    @unittest.skipUnless(running and docked, "Elite Dangerous is not running")
    def test_buy_commodity(self):
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

        res = stn_svc.goto_commodities_market()
        self.assertTrue(res, "Could not access commodities market.")  # add assertion here

        # Find a commodity to buy that is sold by the station
        items = stn_svc.commodities_market.market_parser.get_buyable_items()
        if items is not None:
            # Pick the first item (this will not be the first item in the commodities table)
            name = items[0]['Name_Localised']
        else:
            name = ""

        res = stn_svc.commodities_market.buy_commodity(name, qty=0)
        self.assertTrue(res, "Failed to buy commodity.")  # add assertion here

    @unittest.skipUnless(running and docked, "Elite Dangerous is not running")
    def test_sell_commodity(self):
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

        res = stn_svc.goto_commodities_market()
        self.assertTrue(res, "Could not access commodities market.")  # add assertion here

        # Find a commodity to sell that is bought by the station
        items = stn_svc.commodities_market.market_parser.get_sellable_items()
        if items is not None:
            # Pick the first item (this will not be the first item in the commodities table)
            name = items[0]['Name_Localised']
        else:
            name = ""

        res = stn_svc.commodities_market.sell_commodity(name, qty=0)
        self.assertTrue(res, "Failed to sell commodity.")  # add assertion here

    @unittest.skipUnless(running and docked, "Elite Dangerous is not running")
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
        res = stn_svc.commodities_market.sell_all_commodities()

        self.assertTrue(res, "Failed to sell all commodities.")  # add assertion here


class PersonalTransportMissionsTestCase(unittest.TestCase):
    running = is_running()
    docked = is_docked()

    def test_draw_regions_on_images(self):
        """
        Does NOT require Elite Dangerous to be running.
        ======================================================================
        """
        stn_svc = StationServicesInShip(None, None, None)
        draw_station_regions('test/passenger-lounge/', stn_svc.passenger_lounge.reg)

        self.assertEqual(True, True)  # add assertion here

    @unittest.skipUnless(running and docked, "Elite Dangerous is not running")
    def test_goto_personal_transport_missions(self):
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

        # stn_svc.goto_passenger_lounge()
        res = stn_svc.passenger_lounge.goto_personal_transport_missions()

        self.assertTrue(res, "Failed to goto personal transport missions.")  # add assertion here


if __name__ == '__main__':
    unittest.main()

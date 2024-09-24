from time import sleep

from EDlogger import logger
import json
from pyautogui import typewrite, keyUp, keyDown
from MousePt import MousePoint
from pathlib import Path

"""
File: EDWayPoint.py    

Description:
   Class will load file called waypoints.json which contains a list of System name to jump to.
   Provides methods to select a waypoint pass into it.  

Example file:
    { 
        "Ninabin":   {"DockWithStation": null, "SellItem": -1, "BuyItem": -1, "Completed": false}, 
        "Wailaroju": {"DockWithStation": null, "SellItem": -1, "BuyItem": -1, "Completed": false},
        "Enayex":    {"DockWithStation": "Watt Port", "SellItem": 12, "BuyItem": 5, "Completed": false}, 
        "Eurybia":   {"DockWithStation": null, "SellItem": -1, "BuyItem": -1, "Completed": false} 
    }

Author: sumzer0@yahoo.com
"""


class EDWayPoint:
    def __init__(self, is_odyssey=True):

        self.is_odyssey = is_odyssey
        self.filename = './waypoints.json'
        self.waypoints = {}
        #  { "Ninabin": {"DockWithTarget": false, "TradeSeq": None, "Completed": false} }
        # for i, key in enumerate(self.waypoints):
        # self.waypoints[target]['DockWithTarget'] == True ... then go into SC Assist
        # self.waypoints[target]['Completed'] == True
        # if docked and self.waypoints[target]['Completed'] == False
        #    execute_seq(self.waypoints[target]['TradeSeq'])

        ss = self.read_waypoints()

        # if we read it then point to it, otherwise use the default table above
        if ss is not None:
            self.waypoints = ss
            logger.debug("EDWayPoint: read json:" + str(ss))

        self.num_waypoints = len(self.waypoints)

        # print("waypoints: "+str(self.waypoints))
        self.step = 0

        self.mouse = MousePoint()

    def load_waypoint_file(self, filename=None):
        if filename == None:
            return

        ss = self.read_waypoints(filename)

        if ss is not None:
            self.waypoints = ss
            self.filename = filename
            logger.debug("EDWayPoint: read json:" + str(ss))

    def read_waypoints(self, fileName='./waypoints/waypoints.json'):
        s = None
        try:
            with open(fileName, "r") as fp:
                s = json.load(fp)
        except  Exception as e:
            logger.warning("EDWayPoint.py read_waypoints error :" + str(e))

        return s


    def write_waypoints(self, data, fileName='./waypoints/waypoints.json'):
        if data is None:
            data = self.waypoints
        try:
            with open(fileName, "w") as fp:
                json.dump(data, fp, indent=4)
        except Exception as e:
            logger.warning("EDWayPoint.py write_waypoints error:" + str(e))

    def mark_waypoint_complete(self, key):
        self.waypoints[key]['Completed'] = True
        self.write_waypoints(data=None, fileName='./waypoints/' + Path(self.filename).name)

    def waypoint_next(self, ap, target_select_cb=None) -> str:
        dest_key = "REPEAT"

        # loop back to beginning if last record is "REPEAT"
        while dest_key == "REPEAT":
            for i, key in enumerate(self.waypoints):

                # skip records we already processed
                if i < self.step:
                    continue

                # if this step is marked to skip.. i.e. completed, go to next step
                if self.waypoints[key]['Completed'] == True:
                    continue

                # if this entry is REPEAT, loop through all and mark them all as Completed = False
                if key == "REPEAT":
                    self.mark_all_waypoints_not_complete()
                else:
                    # Call sequence to select route
                    if self.set_waypoint_target(ap, key, target_select_cb) == False:
                        # Error setting target
                        logger.warning("Error setting waypoint, breaking")
                    self.step = i
                dest_key = key

                break
            else:
                dest_key = ""  # End of list, return empty string
        print("test: " + dest_key)
        return dest_key

    def mark_all_waypoints_not_complete(self):
        for j, tkey in enumerate(self.waypoints):
            self.waypoints[tkey]['Completed'] = False
            self.step = 0
        self.write_waypoints(data=None, fileName='./waypoints/' + Path(self.filename).name)

    def is_station_targeted(self, dest) -> bool:
        return self.waypoints[dest]['DockWithStation']

    def set_station_target(self, ap, dest):
        station = self.waypoints[dest]['DockWithStation']
        ap.nav_panel.lock_destination(station)

        # (x, y) = self.waypoints[dest]['StationCoord']
        #
        # # check if StationBookmark exists to get the transition compatibility with old waypoint lists
        # if "StationBookmark" in self.waypoints[dest]:
        #     bookmark = self.waypoints[dest]['StationBookmark']
        # else:
        #     bookmark = -1
        #
        # ap.keys.send('SystemMapOpen')
        # sleep(3.5)
        # if self.is_odyssey and bookmark != -1:
        #     ap.keys.send('UI_Left')
        #     sleep(1)
        #     ap.keys.send('UI_Select')
        #     sleep(.5)
        #     ap.keys.send('UI_Down', repeat=2)
        #     sleep(.5)
        #     ap.keys.send('UI_Right')
        #     sleep(.5)
        #     ap.keys.send('UI_Down', repeat=bookmark)
        #     sleep(.5)
        #     ap.keys.send('UI_Select', hold=4.0)
        # else:
        #     self.mouse.do_click(x, y)
        #     self.mouse.do_click(x, y, 1.25)
        #
        #     # for horizons we need to select it
        #     if self.is_odyssey == False:
        #         ap.keys.send('UI_Select')
        #
        # ap.keys.send('SystemMapOpen')
        # sleep(0.5)

    # Call either the Odyssey or Horizons version of the Galatic Map sequence
    def set_waypoint_target(self, ap, target_name: str, target_select_cb=None) -> bool:
        # No waypoints defined, then return False
        if self.waypoints == None:
            return False

        if self.is_odyssey != True:
            return self.set_waypoint_target_horizons(ap, target_name, target_select_cb)
        else:
            return self.set_waypoint_target_odyssey(ap, target_name, target_select_cb)

    #
    # This sequence for the Horizons
    #
    def set_waypoint_target_horizons(self, ap, target_name: str, target_select_cb=None) -> bool:

        ap.keys.send('GalaxyMapOpen')
        sleep(2)
        ap.keys.send('CycleNextPanel')
        sleep(1)
        ap.keys.send('UI_Select')
        sleep(2)

        typewrite(target_name, interval=0.25)
        sleep(1)

        # send enter key
        ap.keys.send_key('Down', 28)
        sleep(0.05)
        ap.keys.send_key('Up', 28)

        sleep(7)
        ap.keys.send('UI_Right')
        sleep(1)
        ap.keys.send('UI_Select')

        # if got passed through the ship() object, lets call it to see if a target has been
        # selected yet.. otherwise we wait.  If long route, it may take a few seconds
        if target_select_cb != None:
            while not target_select_cb()['target']:
                sleep(1)

        ap.keys.send('GalaxyMapOpen')
        sleep(2)
        return True

    #
    # This sequence for the Odyssey

    def set_waypoint_target_odyssey(self, ap, target_name, target_select_cb=None) -> bool:

        x = ap.scr.screen_width / 2
        y = ap.scr.screen_height / 2

        ap.keys.send('GalaxyMapOpen')
        sleep(2)
        ap.keys.send('UI_Up')
        sleep(.5)
        ap.keys.send('UI_Select')
        sleep(.5)

        # print("Target:"+target_name)
        # type in the System name
        typewrite(target_name, interval=0.25)
        sleep(1)

        # send enter key
        ap.keys.send_key('Down', 28)
        sleep(0.15)
        ap.keys.send_key('Up', 28)

        sleep(1)
        self.mouse.do_click(x, y)
        sleep(0.1)
        ap.keys.send('UI_Right', repeat=4)

        sleep(0.1)

        # go down 6x's to plot to target
        #for i in range(7):  # ED 4.0 update, since have new menu item
        ap.keys.send('UI_Down', repeat=7)
        #    sleep(0.05)

        sleep(0.1)

        # select Plot course
        ap.keys.send('UI_Select')

        # if got passed through the ship() object, lets call it to see if a target has been
        # selected yet.. otherwise we wait.  If long route, it may take a few seconds
        if target_select_cb != None:
            while not target_select_cb()['target']:
                sleep(1)

        sleep(1)

        ap.keys.send('GalaxyMapOpen')
        sleep(1)

        return True

    def execute_trade(self, ap, dest):
        buy_down = self.waypoints[dest]['BuyItem']
        sell_down = self.waypoints[dest]['SellItem']

        if sell_down == "" and buy_down == "":
            return

        # Go to commodities market
        ap.stn_svcs_in_ship.goto_commodities_market()

        # --------- SELL ----------
        if sell_down != "":
            ap.stn_svcs_in_ship.commodities_market.sell_commodity(sell_down, 9999)

        # --------- BUY ----------
        if buy_down != "":
            ap.stn_svcs_in_ship.commodities_market.buy_commodity(buy_down, 9999)

        # Go back to the station services
        ap.stn_svcs_in_ship.goto_ship_view()


# this import the temp class needed for unit testing
"""
from EDKeys import *       
class temp:
    def __init__(self):
        self.keys = EDKeys()
"""

def main():

    # keys   = temp()
    wp  = EDWayPoint(True)  # False = Horizons
    wp.step = 0  # start at first waypoint

    sleep(3)


    
    # dest = 'Enayex'
    # print(dest)

    # print("In waypoint_assist, at:"+str(dest))

    
    # already in doc config, test the trade
    # wp.execute_trade(keys, dest)

    # Set the Route for the waypoint^#
    dest = wp.waypoint_next(ap=None)

    while dest != "":
        #  print("Doing: "+str(dest))
        #  print(wp.waypoints[dest])
        # print("Dock w/station: "+  str(wp.is_station_targeted(dest)))

        # wp.set_station_target(None, dest)

        # Mark this waypoint as complated
        # wp.mark_waypoint_complete(dest)

        # set target to next waypoint and loop)::@
        dest = wp.waypoint_next(ap=None)


if __name__ == "__main__":
    main()

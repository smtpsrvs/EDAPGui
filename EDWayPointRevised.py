from __future__ import annotations

from time import sleep

import cv2

from EDAP_data import *
from EDlogger import logger
import json
from pyautogui import typewrite, keyUp, keyDown
from MousePt import MousePoint
from pathlib import Path

from NavRouteParser import NavRouteParser
from OCR import OCR
from Screen_Regions import reg_scale_for_station
from StatusParser import StatusParser

"""
File: EDWayPointRevised.py    

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


class EDWayPointRevised:
    def __init__(self, is_odyssey=True):
        
        self.is_odyssey = is_odyssey
        self.filename = './waypoints-revised.json'

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
            logger.debug("EDWayPointRevised: read json:"+str(ss))
            
        self.num_waypoints = len(self.waypoints)
     
        #print("waypoints: "+str(self.waypoints))
        self.step = 0
        
        self.mouse = MousePoint()
        self.status = StatusParser()

    def load_waypoint_file(self, filename=None):
        if filename == None:
            return
        
        ss = self.read_waypoints(filename)
        
        if ss is not None:
            self.waypoints = ss
            self.filename = filename
            logger.debug("EDWayPointRevised: read json:"+str(ss))
        
         
    def read_waypoints(self, fileName='./waypoints/waypoints-revised.json'):
        s = None
        try:
            with open(fileName,"r") as fp:
                s = json.load(fp)
        except  Exception as e:
            logger.warning("EDWayPointRevised.py read_waypoints error :" + str(e))

        return s    
       

    def write_waypoints(self, data, fileName='./waypoints/waypoints-revised.json'):
        if data is None:
            data = self.waypoints
        try:
            with open(fileName,"w") as fp:
                json.dump(data,fp, indent=4)
        except Exception as e:
            logger.warning("EDWayPointRevised.py write_waypoints error:" + str(e))

    def mark_waypoint_complete(self, key):
        self.waypoints[key]['Completed'] = True
        self.write_waypoints(data=None, fileName='./waypoints/' + Path(self.filename).name)  

    def get_waypoint(self):
        """ Returns the next waypoint list or None if we are at the end of the waypoints.
        """
        dest_key = "-1"

        # loop back to beginning if last record is "REPEAT"
        while dest_key == "-1":
            for i, key in enumerate(self.waypoints):
                # skip records we already processed
                if i < self.step:
                    continue

                # if this entry is REPEAT, mark them all as Completed = False
                if self.waypoints[key]['System'] == "REPEAT":
                    self.mark_all_waypoints_not_complete()
                    break

                # if this step is marked to skip.. i.e. completed, go to next step
                if self.waypoints[key]['Completed']:
                    continue

                # This is the next uncompleted step
                self.step = i
                dest_key = key
                break
            else:
                return None, None

        return dest_key, self.waypoints[dest_key]

    def set_next_system(self, ap, target_system) -> bool:
        """ Sets the next system to jump to, or the final system to jump to.
        If the system is already selected or is selected correctly, returns True,
        otherwise False.
        """
        # Call sequence to select route
        if self.set_waypoint_target(ap, target_system, None):
            return True
        else:
            # Error setting target
            logger.warning("Error setting waypoint, breaking")
            return False

    def waypoint_next(self, ap, target_select_cb=None) -> str:
        """ Sets the destination system in the galaxy map and return the key.
        """
        dest_key = "-1"

        # loop back to beginning if last record is "REPEAT"
        while dest_key == "-1":
            for i, key in enumerate(self.waypoints):

                # skip records we already processed
                if i < self.step:
                    continue

                # if this step is marked to skip.. i.e. completed, go to next step
                if self.waypoints[key]['Completed']:
                    continue

                # if this entry is REPEAT, loop through all and mark them all as Completed = False
                if self.waypoints[key]['System'] == "REPEAT":
                    self.mark_all_waypoints_not_complete()
                else:
                    # Don't set system in galaxy map if we are in system
                    if self.waypoints[key]['System'].upper() != ap.jn.ship_state()['cur_star_system'].upper():
                        # Call sequence to select route
                        if not self.set_waypoint_target(ap, self.waypoints[key]['System'], target_select_cb):
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

        # Call either the Odyssey or Horizons version of the Galatic Map sequence

    def set_waypoint_target(self, ap, target_system: str, target_select_cb=None) -> bool:
        """ Set System target using galaxy map """
        if self.is_odyssey != True:
            return self.set_waypoint_target_horizons(ap, target_system, target_select_cb)
        else:
            return self.set_waypoint_target_odyssey(ap.scr, ap.keys, target_system, target_select_cb)

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

    def set_waypoint_target_odyssey(self, scr, keys, target_system, target_select_cb=None) -> bool:
        # TODO - separate the functions for the gal map to a separate class
        # Get the current route (system name or None)
        nav_route_parser = NavRouteParser()
        targeted_system = nav_route_parser.get_last_system()
        if targeted_system is not None:
            # Check if the correct system is already targeted
            if targeted_system.upper() == target_system.upper():
                return True

        # Open Galaxy Map if we are not there.
        status_data = self.status.get_cleaned_data()
        if status_data['GuiFocus'] != GuiFocusGalaxyMap:
            keys.send('GalaxyMapOpen')
            sleep(2)
            keys.send('UI_Up')
        else:
            keys.send('UI_Left', repeat=2)
            keys.send('UI_Right')

        sleep(.5)
        keys.send('UI_Select')
        sleep(.5)

        # print("Target:"+target_name)
        # type in the System name
        typewrite(target_system, interval=0.25)
        sleep(1)

        # send enter key
        keys.send_key('Down', 28)  # 28=ENTER
        sleep(0.15)
        keys.send_key('Up', 28)  # 28=ENTER

        sleep(0.1)

        # This seems to be the way to get this to work when there is only one match for the
        # system and when there are multiple. Just hitting enter does not work consistently.
        #keys.send('UI_Down') # Select the first item in the drop down
        #keys.send('UI_Up') # Back to entry box
        keys.send('UI_Right')  # Select the right arrow on search bar

        # Check if the selected system is the actual system or one starting with the same char's
        # i.e. We want LHS 54 and the system list gives us LHS 547, LHS 546 and LHS 54
        system_name = self.get_system_from_system_info_panel(scr, target_system)
        if system_name is None:
            logger.debug("Could not find SYSTEM INFO panel. Check the INFO panel is shown.")
            return False

        if system_name.upper() == target_system.upper():
            logger.debug("Target found in system info panel: " + system_name)
            res = True
        else:
            res = False

        tries = 0
        last_system = ""
        # Cycle through all systems matching the current filter
        while not res:
            keys.send('UI_Select')  # CLick to go to next system in the list
            sleep(0.25)  # The info panel updates before the system comes to center
            system_name = self.get_system_from_system_info_panel(scr, target_system)
            logger.debug(f"Target system: {target_system.upper()}. Current system: {system_name}")

            # Break loop and continue if this is a match
            if system_name.upper() == target_system.upper():
                break

            # Check if we are stuck on the same system
            if system_name == last_system:
                tries = tries + 1
                # Quit after some attempts
                if tries > 3:
                    return False
            else:
                tries = 0
                last_system = system_name

        # zoom camera which puts focus back on the map
        keys.send('CamZoomIn')
        # plot route. Not that once the system has been selected, as shown in the info panel
        # and the gal map has focus, there is no need to wait for the map to bring the system
        # to the center screen, the system can be selected while the map is moving.
        keys.send('UI_Select', hold=0.75)

        sleep(0.05)

        # if got passed through the ship() object, lets call it to see if a target has been
        # selected yet.. otherwise we wait.  If long route, it may take a few seconds
        if target_select_cb is not None:
            while not target_select_cb()['target']:
                sleep(1)

        sleep(1)

        keys.send('GalaxyMapOpen')
        sleep(1)

        return True

    def get_system_from_system_info_panel(self, scr, system_name: str) -> str | None:
        """ Get the system name from the System Info panel of the Galaxy Map.
        Returns a string containing the system name, or None if the panel does not appear
        or the system could not be determined. """
        # TODO - move to galaxy map class
        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution at 1920x1080
        reg = {'gal_map_system_info': {'rect': [0.695, 0.155, 0.935, 0.26]},
               'gal_map_powerplay_info': {'rect': [0.64, 0.155, 0.935, 0.26]}}

        # Scale the regions based on the target resolution.
        scl_sys_reg_rect = reg_scale_for_station(reg['gal_map_system_info'], scr.screen_width, scr.screen_height)
        scl_pp_reg_rect = reg_scale_for_station(reg['gal_map_powerplay_info'], scr.screen_width, scr.screen_height)

        ocr = OCR(scr)
        # Capture both images
        image_pp = ocr.capture_region(scl_pp_reg_rect)
        cv2.imwrite(f'test/gal_map_powerplay_info.png', image_pp)

        image_sys = ocr.capture_region(scl_sys_reg_rect)
        cv2.imwrite(f'test/gal_map_system_info.png', image_sys)

        # Check if this is the POWERPLAY INFORMATION panel first as this is the wider of the two
        ocr_textlist = ocr.image_simple_ocr(image_pp)
        if ocr_textlist is None:
            return None

        is_powerplay = False
        # Check if this is the POWERPLAY INFO panel
        for s in ocr_textlist:
            if s.startswith("POWERPLAY"):
                is_powerplay = True
                break

        # If not the POWERPLAY INFO panel, OCR the smaller SYSTEM INFO panel image.
        if not is_powerplay:
            ocr_textlist = ocr.image_simple_ocr(image_sys)
            if ocr_textlist is None:
                return None

        # Process OCR list which should be in the following form:
        #   SYSTEM INFORMATION / MARKET / STORED SHIPS / FRIENDS / THARGOID
        #   System Name
        #   DISTANCE: x.xxLY
        # Sometimes systems come in as ['LHS 54'] and sometimes ['LHS','54']
        info_pnl_found = False
        system = ""
        for s in ocr_textlist:
            # Check each of the INFO panel titles
            if (s.startswith("POWERPLAY") or s.startswith("SYSTEM") or s.startswith("MARKET") or
                    s.startswith("INFORMATION") or s.startswith("STORED") or s.startswith("SHIPS") or
                    s.startswith("FRIENDS") or s.startswith("THARGOID")):
                # Do nothing
                info_pnl_found = True
                system = system
            elif s.startswith("LAST UPDATED") or s.startswith("DISTANCE"):
                info_pnl_found = True
                break
            else:
                if system == "":
                    # Set first part
                    system = s
                else:
                    # Append next part
                    system = system + " " + s

        # Return None if the info panel did not appear
        if not info_pnl_found:
            return None

        # Return the system name
        return system

    def execute_trade(self, ap, dest_key):
        buy_down = self.waypoints[dest_key]['BuyItem']
        sell_down = self.waypoints[dest_key]['SellItem']

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
    #keys   = temp()
    wp = EDWayPointRevised(True)  # False = Horizons
    wp.step = 0  #start at first waypoint

    sleep(3)

    #dest = 'Enayex'
    #print(dest)

    #print("In waypoint_assist, at:"+str(dest))

    # already in doc config, test the trade
    #wp.execute_trade(keys, dest)    

    # Set the Route for the waypoint^#
    while 1:
        dest = wp.get_waypoint()
        print("Doing: " + str(dest))
        if dest is None:
            break

    #  print(wp.waypoints[dest])
    # print("Dock w/station: "+  str(wp.is_station_targeted(dest)))

    #wp.set_station_target(None, dest)

    # Mark this waypoint as complated
    #wp.mark_waypoint_complete(dest)

    # set target to next waypoint and loop)::@
    #dest = wp.get_next_waypoint()


if __name__ == "__main__":
    main()

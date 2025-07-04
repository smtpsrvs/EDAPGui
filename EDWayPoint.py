from __future__ import annotations
from time import sleep
from CargoParser import CargoParser
from EDAP_data import *
from EDKeys import EDKeys
from EDlogger import logger
import json
from MarketParser import MarketParser
from MousePt import MousePoint
from pathlib import Path

"""
File: EDWayPoint.py    

Description:
   Class will load file called waypoints.json which contains a list of System name to jump to.
   Provides methods to select a waypoint pass into it.  

Author: sumzer0@yahoo.com
"""


class EDWayPoint:
    def __init__(self, ed_ap, is_odyssey=True):
        self.ap = ed_ap
        self.is_odyssey = is_odyssey
        self.filename = './waypoints.json'
        self.stats_log = {'Colonisation': 0, 'Construction': 0, 'Fleet Carrier': 0, 'Station': 0}
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
        self.market_parser = MarketParser()
        self.cargo_parser = CargoParser()

    def load_waypoint_file(self, filename=None) -> bool:
        if filename is None:
            return False

        ss = self.read_waypoints(filename)

        if ss is not None:
            self.waypoints = ss
            self.filename = filename
            self.ap.ap_ckb('log', f"Loaded Waypoint file: {filename}")
            logger.debug("EDWayPoint: read json:" + str(ss))
            return True

        self.ap.ap_ckb('log', f"Waypoint file is invalid. Check log file for details.")
        return False

    def read_waypoints(self, filename='./waypoints/waypoints.json'):
        s = None
        try:
            with open(filename, "r") as fp:
                s = json.load(fp)

            # Perform any checks on the data returned
            # Check if the waypoint data contains the 'GlobalShoppingList' (new requirement)
            if 'GlobalShoppingList' not in s:
                # self.ap.ap_ckb('log', f"Waypoint file is invalid. Check log file for details.")
                logger.warning(f"Waypoint file {filename} is invalid or old version. "
                               f"It does not contain a 'GlobalShoppingList' waypoint.")
                s = None

            # Check the
            err = False
            for key, value in s.items():
                if key == 'GlobalShoppingList':
                    # Special case
                    if 'BuyCommodities' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'BuyCommodities'.")
                        err = True
                    if 'UpdateCommodityCount' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'UpdateCommodityCount'.")
                        err = True
                    if 'Skip' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'Skip'.")
                        err = True
                else:
                    # All other cases
                    if 'SystemName' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'SystemName'.")
                        err = True
                    if 'StationName' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'StationName'.")
                        err = True
                    if 'GalaxyBookmarkType' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'GalaxyBookmarkType'.")
                        err = True
                    if 'GalaxyBookmarkNumber' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'GalaxyBookmarkNumber'.")
                        err = True
                    if 'SystemBookmarkType' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'SystemBookmarkType'.")
                        err = True
                    if 'SystemBookmarkNumber' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'SystemBookmarkNumber'.")
                        err = True
                    if 'SellCommodities' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'SellCommodities'.")
                        err = True
                    if 'BuyCommodities' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'BuyCommodities'.")
                        err = True
                    if 'UpdateCommodityCount' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'UpdateCommodityCount'.")
                        err = True
                    if 'FleetCarrierTransfer' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'FleetCarrierTransfer'.")
                        err = True
                    if 'Skip' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'Skip'.")
                        err = True
                    if 'Completed' not in value:
                        logger.warning(f"Waypoint file key '{key}' does not contain 'Completed'.")
                        err = True

            if err:
                s = None

        except Exception as e:
            logger.warning("EDWayPoint.py read_waypoints error :" + str(e))

        return s

    def write_waypoints(self, data, filename='./waypoints/waypoints.json'):
        if data is None:
            data = self.waypoints
        try:
            with open(filename, "w") as fp:
                json.dump(data, fp, indent=4)
        except Exception as e:
            logger.warning("EDWayPoint.py write_waypoints error:" + str(e))

    def mark_waypoint_complete(self, key):
        self.waypoints[key]['Completed'] = True
        self.write_waypoints(data=None, filename='./waypoints/' + Path(self.filename).name)

    def get_waypoint(self) -> tuple[str, dict] | tuple[None, None]:
        """ Returns the next waypoint list or None if we are at the end of the waypoints.
        """
        dest_key = "-1"

        # loop back to beginning if last record is "REPEAT"
        while dest_key == "-1":
            for i, key in enumerate(self.waypoints):
                # skip records we already processed
                if i < self.step:
                    continue

                # if this entry is REPEAT (and not skipped), mark them all as Completed = False
                if ((self.waypoints[key].get('SystemName', "").upper() == "REPEAT")
                        and not self.waypoints[key]['Skip']):
                    self.mark_all_waypoints_not_complete()
                    break

                # if this step is marked to skip... i.e. completed, go to next step
                if (key == "GlobalShoppingList" or self.waypoints[key]['Completed']
                        or self.waypoints[key]['Skip']):
                    continue

                # This is the next uncompleted step
                self.step = i
                dest_key = key
                break
            else:
                return None, None

        return dest_key, self.waypoints[dest_key]

    def mark_all_waypoints_not_complete(self):
        for j, tkey in enumerate(self.waypoints):
            # Ensure 'Completed' key exists before trying to set it
            if 'Completed' in self.waypoints[tkey]:
                self.waypoints[tkey]['Completed'] = False
            else:
                # Handle legacy format where 'Completed' might be missing
                # Or log a warning if the structure is unexpected
                logger.warning(f"Waypoint {tkey} missing 'Completed' key during reset.")
            self.step = 0
        self.write_waypoints(data=None, filename='./waypoints/' + Path(self.filename).name)
        self.log_stats()

    def log_stats(self):
        calc1 = 1.5 ** self.stats_log['Colonisation']
        calc2 = 1.5 ** self.stats_log['Construction']
        sleep(max(calc1, calc2))

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
        ap.ship_control.goto_cockpit_view()

    def waypoint_assist(self, keys, scr_reg):
        """ Processes the waypoints, performing jumps and sc assist if going to a station
        also can then perform trades if specific in the waypoints file.
        """
        if len(self.waypoints) == 0:
            self.ap.ap_ckb('log+vce', "No Waypoint file loaded. Exiting Waypoint Assist.")
            return

        self.step = 0  # start at first waypoint
        self.ap.ap_ckb('log', "Waypoint file: " + str(Path(self.filename).name))
        self.reset_stats()

        # Loop until complete, or error
        _abort = False
        while not _abort:
            # Current location
            cur_star_system = self.ap.jn.ship_state()['cur_star_system'].upper()
            cur_station = self.ap.jn.ship_state()['cur_station'].upper()
            cur_station_type = self.ap.jn.ship_state()['cur_station_type'].upper()

            # Current in game destination
            status = self.ap.status.get_cleaned_data()
            destination_system = status['Destination_System']  # The system ID
            destination_body = status['Destination_Body']  # The body number (0 for prim star)
            destination_name = status['Destination_Name']  # The system/body/station/settlement name

            # ====================================
            # Get next Waypoint
            # ====================================

            # Get the waypoint details
            old_step = self.step
            dest_key, next_waypoint = self.get_waypoint()
            if dest_key is None:
                self.ap.ap_ckb('log+vce', "Waypoint list has been completed.")
                break

            # Is this a new waypoint?
            if self.step != old_step:
                new_waypoint = True
            else:
                new_waypoint = False

            # Flag if we are using bookmarks
            gal_bookmark = next_waypoint.get('GalaxyBookmarkNumber', -1) > 0
            sys_bookmark = next_waypoint.get('SystemBookmarkNumber', -1) > 0
            gal_bookmark_type = next_waypoint.get('GalaxyBookmarkType', '')
            gal_bookmark_num = next_waypoint.get('GalaxyBookmarkNumber', 0)
            sys_bookmark_type = next_waypoint.get('SystemBookmarkType', '')
            sys_bookmark_num = next_waypoint.get('SystemBookmarkNumber', 0)

            next_wp_system = next_waypoint.get('SystemName', '').upper()
            next_wp_station = next_waypoint.get('StationName', '').upper()

            if new_waypoint:
                self.ap.ap_ckb('log+vce', f"Next Waypoint: {next_wp_station} in {next_wp_system}")

            # ====================================
            # Target and travel to a System
            # ====================================

            # Check current system and go to next system if different and not blank
            if next_wp_system == "" or (cur_star_system == next_wp_system):
                if new_waypoint:
                    self.ap.ap_ckb('log+vce', f"Already in target System.")
            else:
                # Check if the current nav route is to the target system
                last_nav_route_sys = self.ap.nav_route.get_last_system().upper()
                # Check we have a route and that we have a destination to a star (body 0).
                # We can have one without the other.
                if ((last_nav_route_sys == next_wp_system) and
                        (destination_body == 0 and destination_name != "")):
                    # No need to target system
                    self.ap.ap_ckb('log+vce', f"System already targeted.")
                else:
                    self.ap.ap_ckb('log+vce', f"Targeting system {next_wp_system}.")
                    # Select destination in galaxy map based on name
                    res = self.ap.galaxy_map.set_gal_map_destination_text(self.ap, next_wp_system,
                                                                          self.ap.jn.ship_state)
                    if res:
                        self.ap.ap_ckb('log', f"System has been targeted.")
                    else:
                        self.ap.ap_ckb('log+vce', f"Unable to target {next_wp_system} in Galaxy Map.")
                        _abort = True
                        break

                # Select next target system
                # TODO should this be in before every jump?
                keys.send('TargetNextRouteSystem')

                # Jump to the destination system
                self.ap.ap_ckb('log+vce', f"Jumping to {next_wp_system}.")
                res = self.ap.jump_to_system(scr_reg, next_wp_system)
                if not res:
                    self.ap.ap_ckb('log', f"Failed to jump to {next_wp_system}.")
                    _abort = True
                    break

                continue

            # ====================================
            # Target and travel to a local Station
            # ====================================

            # If we are in the right system, check if we are already docked.
            docked_at_stn = False
            is_docked = self.ap.status.get_flag(FlagsDocked)
            if is_docked:
                # Check if we are at the correct station. Note that for FCs, the station name
                # reported by the Journal is only the ship identifier (ABC-123) and not the carrier name.
                # So we need to check if the ID (ABC-123) is at the end of the target ('Fleety McFleet ABC-123').
                if cur_station_type == 'FleetCarrier'.upper():
                    docked_at_stn = next_wp_station.endswith(cur_station)
                elif next_wp_station == 'System Colonisation Ship'.upper():
                    if (cur_station_type == 'SurfaceStation'.upper() and
                            'ColonisationShip'.upper() in cur_station.upper()):
                        docked_at_stn = True
                # elif next_wp_station.startswith('Orbital Construction Site'.upper()):
                #     if (cur_station_type == 'SurfaceStation'.upper() and
                #             'Orbital Construction Site'.upper() in cur_station.upper()):
                #         docked_at_stn = True
                elif cur_station == next_wp_station:
                    docked_at_stn = True

            # Check current station and go to it if different
            if docked_at_stn:
                if new_waypoint:
                    self.ap.ap_ckb('log+vce', f"Already at target Station: {next_wp_station}")
            else:
                # Check if we need to travel to a station, else we are done.
                # This may be by 1) System bookmark, 2) Galaxy bookmark or 3) by Station Name text
                if sys_bookmark or gal_bookmark or next_wp_station != "":
                    # If waypoint file has a Station Name associated then attempt targeting it
                    self.ap.ap_ckb('log+vce', f"Targeting Station: {next_wp_station}")

                    if gal_bookmark:
                        # Set destination via gal bookmark, not system bookmark
                        res = self.ap.galaxy_map.set_gal_map_dest_bookmark(self.ap, gal_bookmark_type, gal_bookmark_num)
                        if not res:
                            self.ap.ap_ckb('log+vce', f"Unable to set Galaxy Map bookmark.")
                            _abort = True
                            break

                    elif sys_bookmark:
                        # Set destination via system bookmark
                        res = self.ap.system_map.set_sys_map_dest_bookmark(self.ap, sys_bookmark_type, sys_bookmark_num)
                        if not res:
                            self.ap.ap_ckb('log+vce', f"Unable to set System Map bookmark.")
                            _abort = True
                            break

                    elif next_wp_station != "":
                        # Need OCR added in for this (WIP)
                        need_ocr = True
                        self.ap.ap_ckb('log+vce', f"No bookmark defined. Target by Station text not supported.")
                        # res = self.nav_panel.lock_destination(station_name)
                        _abort = True
                        break

                    # Jump to the station by name
                    res = self.ap.supercruise_to_station(scr_reg, next_wp_station)
                    sleep(1)  # Allow status log to update
                    continue
                else:
                    self.ap.ap_ckb('log+vce', f"Arrived at target System: {next_wp_system}")

            # ====================================
            # Dock and Trade at Station
            # ====================================

            # Are we at the correct station to trade?
            if docked_at_stn:  # and (next_wp_station != "" or sys_bookmark):
                # Docked - let do trade
                self.ap.ap_ckb('log+vce', f"Execute trade at Station: {next_wp_station}")
                self.execute_trade(self.ap, dest_key)

            # Mark this waypoint as completed
            self.mark_waypoint_complete(dest_key)
            self.ap.ap_ckb('log+vce', f"Current Waypoint complete.")

        # Done with waypoints
        if not _abort:
            self.ap.ap_ckb('log+vce',
                           "Waypoint Route Complete, total distance jumped: " + str(self.ap.total_dist_jumped) + "LY")
            self.ap.update_ap_status("Idle")
        else:
            self.ap.ap_ckb('log+vce', "Waypoint Route was aborted.")
            self.ap.update_ap_status("Idle")

    def reset_stats(self):
        # Clear stats
        self.stats_log['Colonisation'] = 0
        self.stats_log['Construction'] = 0
        self.stats_log['Fleet Carrier'] = 0
        self.stats_log['Station'] = 0


def main():
    from ED_AP import EDAutopilot

    ed_ap = EDAutopilot(cb=None)
    wp = EDWayPoint(ed_ap, True)  # False = Horizons
    wp.step = 0  # start at first waypoint
    keys = EDKeys(cb=None)
    keys.activate_window = True
    wp.ap.stn_svcs_in_ship.select_sell(keys)
    wp.ap.stn_svcs_in_ship.sell_commodity(keys, "Aluminium", 1, wp.cargo_parser)
    wp.ap.stn_svcs_in_ship.sell_commodity(keys, "Beryllium", 1, wp.cargo_parser)
    wp.ap.stn_svcs_in_ship.sell_commodity(keys, "Cobalt", 1, wp.cargo_parser)
    #wp.ap.stn_svcs_in_ship.buy_commodity(keys, "Titanium", 5, 200)

    # dest = 'Enayex'
    #print(dest)

    #print("In waypoint_assist, at:"+str(dest))

    # already in doc config, test the trade
    #wp.execute_trade(keys, dest)

    # Set the Route for the waypoint^#
    #dest = wp.waypoint_next(ap=None)

    #while dest != "":

    #  print("Doing: "+str(dest))
    #  print(wp.waypoints[dest])

    #wp.set_station_target(None, dest)

    # Mark this waypoint as complated
    #wp.mark_waypoint_complete(dest)

    # set target to next waypoint and loop
    #dest = wp.waypoint_next(ap=None)


if __name__ == "__main__":
    main()

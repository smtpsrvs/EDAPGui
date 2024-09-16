from time import sleep
import time

'''
import keyboard
import win32gui

import Screen_Regions
from ED_AP import *
from EDJournal import *
from EDKeys import *
from EDlogger import logger
from Image_Templates import *
from Overlay import *
from Screen import *
from Voice import *
'''

"""
File:Robigo.py   

Description:
This class contains the script required to execute the Robigo passenger mission loop

Constraints:
- Odyssey only (due to unique Mission Selection and Mission Completion menus)
- In first run most verify that Sirius Atmospherics is in the Nav Panel after entering the Sothis System
  - if not 'end' the Robigo Assist,  Target 'Don's Inheritence'  Supercuise there, when < 1000 ls 
    Sirius Athmospherics will be in the Nav Panel, select it, and restart Robigo Assist
- Set Nav Menu Filter to: Stations and POI only
    - Removes the clutter and allows faster selection of Robigo Mines and Sirius Athmos
- Set refuelthreshold low.. like 35%  so not attempt refuel with a ship that doesn't have fuel scoop

Author: sumzer0@yahoo.com
"""

# TODO:  

#  - Robigo Mines SC:  Sometimes Robigo mines are other side of the ring when approaching
#  - to fix this for Horizon, would have to write new routines for get_missions() and complete_missions
#     then similar to Waypoints use the         if is_odyssey != True:   to call the right routine
#


# define the states of the Robigo loop, allow to reenter same state left off if
# having to cancel the AP but want to restart where you left off
STATE_MISSIONS = 1
STATE_ROUTE_TO_SOTHIS = 2
STATE_UNDOCK = 3
STATE_FSD_TO_SOTHIS = 4
STATE_TARGET_SIRIUS = 5
STATE_SC_TO_SIRIUS = 6
STATE_ROUTE_TO_ROBIGO = 7
STATE_FSD_TO_ROBIGO = 8
STATE_TARGET_ROBIGO_MINES = 9
STATE_SC_TO_ROBIGO_MINES = 10


class Robigo:
    def __init__(self, ed_ap):
        self.ap = ed_ap
        self.mission_redirect = 0
        self.mission_complete = 0
        self.state = STATE_MISSIONS  # default to turn in missions and get more
        self.do_single_loop = False  # default is to continue to loop

    def set_single_loop(self, single_loop):
        self.do_single_loop = single_loop

    # Turn in Missions, will do Credit only
    def complete_missions(self, ap):

        # get how many missions were completed, @sirius atmospherics, this mission_redirected will
        # update for each mission you selected
        loop_missions = ap.jn.ship_state()['mission_redirected']
        if loop_missions == 0:
            loop_missions = 8
        ap.jn.ship_state()['mission_completed'] = 0

        # Check if "NO COMPLETED MISSIONS" is shown in the passenger lounge
        found = self.ap.stn_svcs_in_ship.passenger_lounge.missions_ready_to_complete()
        if not found:
            print("No missions to complete")
            ap.keys.send("UI_Left")
            return

        # Go to complete missions
        ap.keys.send("UI_Right", repeat=2)  # go to Complete Mission
        ap.keys.send("UI_Select")
        sleep(2)  # give time for mission page to come up

        while True:
            found = self.ap.stn_svcs_in_ship.passenger_lounge.find_mission_to_complete()
            if found:
                ap.keys.send("UI_Select")  # select mission
                sleep(0.1)
                ap.keys.send("UI_Up")  # Up to Credit
                sleep(0.1)
                ap.keys.send("UI_Select")  # Select it
                sleep(10)  # wait until the "skip" button changes to "back" button
                ap.keys.send("UI_Select")  # Select the Back key which will be highlighted
                sleep(1.5)
            else:
                break

        ap.keys.send("UI_Back")  # seem to be going back to Mission menu

    # Finish the selection of the mission by assigning to a Cabin
    # Will use the Auto fill which doesn't do a very good job optimizing the cabin fill
    def select_mission(self, ap):
        ap.keys.send("UI_Select", repeat=2)  # select mission and Pick Cabin
        ap.keys.send("UI_Down")  # move down to Auto Fill line
        sleep(0.1)
        ap.keys.send("UI_Right", repeat=2)  # go over to "Auto Fill"
        ap.keys.send("UI_Select")  # Select auto fill
        sleep(0.1)
        ap.keys.send("UI_Select")  # Select Accept Mission, which was auto highlighted

    # Goes through the missions selecting any that are Sirius Atmos
    def get_missions(self, ap):
        mission_cnt = 0

        self.ap.stn_svcs_in_ship.passenger_lounge.goto_personal_transport_missions()

        # Loop selecting missions, go up to 20 times, have seen at time up to 17 missions
        # before getting to Sirius Atmos missions
        while mission_cnt < 20:
            found = self.ap.stn_svcs_in_ship.passenger_lounge.select_mission_with_dest("SIRIUS ATMOSPHERICS")

            # found a sirius mission
            if found:
                mission_cnt += 1  # found a mission, select it
                self.select_mission(ap)
                sleep(1.5)
            else:
                break

        # Check if no missions were found.
        if mission_cnt == 0:
            ap.update_ap_status("No missions found!")

        ap.keys.send("UI_Back", repeat=4)  # go back to main menu              

    # SC to the Marker and retrieve num of missions redirected (i.e. completed)
    def travel_to_sirius_atmos(self, ap):

        ap.jn.ship_state()['mission_redirected'] = 0
        self.mission_redirected = 0

        # at times when coming out of SC, we are still 700-800km away from Sirius Atmos
        # if we do not get mission_redirected journal notices, then SC again
        while self.mission_redirected == 0:
            # SC to Marker, tell assist not to attempt docking since we are going to a marker
            ap.sc_assist(ap.scrReg, do_docking=False)

            # wait until we are back in_space
            while ap.jn.ship_state()['status'] != 'in_space':
                sleep(1)

            # give a few more seconds
            sleep(2)
            ap.keys.send("SetSpeedZero")
            ap.keys.send("SelectTarget")  # target the marker so missions will complete
            # takes about 10-22 sec to acknowledge missions
            sleep(15)
            if ap.jn.ship_state()['mission_redirected'] == 0:
                print("Didnt make it to sirius atmos, should SC again")

            self.mission_redirected = ap.jn.ship_state()['mission_redirected']

    # Determine where we are at in the Robigo Loop, return the corresponding state
    def determine_state(self, ap) -> int:
        state = STATE_MISSIONS
        status = ap.jn.ship_state()['status']
        target = ap.jn.ship_state()['target']
        location = ap.jn.ship_state()['location']
        body = ap.jn.ship_state()['body']

        if status == 'in_station':
            state = STATE_MISSIONS
            if target != None:  # seems we already have a target
                state = STATE_UNDOCK
        elif status == 'in_space' and location == 'Robigo' and target != None:
            state = STATE_FSD_TO_SOTHIS
        elif status == 'in_space' and location == 'Sothis' and body == 'Sothis A 5':
            if target == None:
                state = STATE_ROUTE_TO_ROBIGO
            else:
                state = STATE_FSD_TO_ROBIGO
        elif location == 'Sothis' and status == 'in_supercruise':
            state = STATE_SC_TO_SIRIUS
        elif location == 'Robigo' and status == 'in_supercruise':
            state = STATE_SC_TO_ROBIGO_MINES
        elif location != 'Robigo' and location != 'Sothis':
            # we are in neither system, and using default state, so lets target
            # Robigo and FSD there             
            if self.state == STATE_MISSIONS:  # default state, then go back to Robigo
                state = STATE_ROUTE_TO_ROBIGO
            else:
                # else we are between the systems, so lets just use the last state we were in
                # either FSD_TO_ROBIGO or FSD_TO_SOTHIS
                state = self.state  # other wise go back to last state

        return state

    # The Robigo Loop
    def loop(self, ap):
        loop_cnt = 0

        start_time = time.time()

        self.state = self.determine_state(ap)

        while True:

            if self.state == STATE_MISSIONS:
                if not self.do_single_loop:  # if looping, then do mission processing
                    ap.update_ap_status("Completing missions")

                    # Complete Missions, if we have any
                    self.ap.stn_svcs_in_ship.goto_passenger_lounge()
                    sleep(2.5)  # wait for new menu comes up
                    self.complete_missions(ap)

                    ap.update_ap_status("Get missions")
                    # Select and fill up on Sirius missions   
                    #self.ap.station_services_in_ship.goto_passenger_lounge()
                    #sleep(1)
                    self.get_missions(ap)
                self.state = STATE_ROUTE_TO_SOTHIS

            elif self.state == STATE_ROUTE_TO_SOTHIS:
                ap.update_ap_status("Route to SOTHIS")
                # Target SOTHIS and plot route
                ap.jn.ship_state()["target"] = None  # must clear out previous target from Journal
                dest = ap.waypoint.set_waypoint_target(ap, "SOTHIS ", target_select_cb=ap.jn.ship_state)

                if dest == False:
                    ap.update_ap_status("SOTHIS not set: " + str(dest))
                    break

                sleep(1)  # give time to popdown GalaxyMap
                self.state = STATE_UNDOCK

            elif self.state == STATE_UNDOCK:
                # if we got the destination and perform undocking
                ap.keys.send("SetSpeedZero")  # ensure 0 so auto undock will work 

                ap.waypoint_undock_seq()
                self.state = STATE_FSD_TO_SOTHIS

            elif self.state == STATE_FSD_TO_SOTHIS:
                ap.update_ap_status("FSD to SOTHIS")

                # away from station, time for Route Assist to get us to SOTHIS
                ap.fsd_assist(ap.scrReg)
                ap.keys.send("SetSpeed50")  # reset speed
                self.state = STATE_TARGET_SIRIUS

            elif self.state == STATE_TARGET_SIRIUS:
                ap.update_ap_status("Target Sirius")
                # [In Sothis]
                # select Siruis Atmos
                found = ap.nav_panel.lock_destination("SIRIUS ATMOSPHERICS")
                if not found:
                    ap.update_ap_status("No Sirius Atmos in Nav Panel")
                    return
                self.state = STATE_SC_TO_SIRIUS

            elif self.state == STATE_SC_TO_SIRIUS:
                ap.update_ap_status("SC to Marker")
                self.travel_to_sirius_atmos(ap)

                ap.update_ap_status("Missions: " + str(self.mission_redirected))
                self.state = STATE_ROUTE_TO_ROBIGO

            elif self.state == STATE_ROUTE_TO_ROBIGO:
                ap.update_ap_status("Route to Robigo")
                # Set Route back to Robigo
                dest = ap.waypoint.set_waypoint_target(ap, "ROBIGO", target_select_cb=ap.jn.ship_state)
                sleep(2)

                if dest == False:
                    ap.update_ap_status("Robigo not set: " + str(dest))
                    break

                self.state = STATE_FSD_TO_ROBIGO

            elif self.state == STATE_FSD_TO_ROBIGO:
                ap.update_ap_status("FSD to Robigo")
                # have Route Assist bring us back to Robigo system
                ap.fsd_assist(ap.scrReg)
                ap.keys.send("SetSpeed50")
                sleep(2)
                self.state = STATE_TARGET_ROBIGO_MINES

            elif self.state == STATE_TARGET_ROBIGO_MINES:
                ap.update_ap_status("Target Robigo Mines")
                # In Robigo System, select Robigo Mines in the Nav Panel, which should 1 down (we select in the blind)
                #   The Robigo Mines position in the list is dependent on distance from current location
                #   The Speed50 above and waiting 2 seconds ensures Robigo Mines is 2 down from top
                found = ap.nav_panel.lock_destination("ROBIGO MINES")
                if not found:
                    ap.update_ap_status("No lock on Robigo Mines in Nav Panel")
                    return
                self.state = STATE_SC_TO_ROBIGO_MINES

            elif self.state == STATE_SC_TO_ROBIGO_MINES:
                ap.update_ap_status("SC to Robigo Mines")
                # SC Assist to Robigo Mines and dock
                ap.sc_assist(ap.scrReg)

                # Calc elapsed time for a loop and display it
                elapsed_time = time.time() - start_time
                start_time = time.time()
                loop_cnt += 1
                if loop_cnt != 0:
                    ap.ap_ckb('log', "Loop: " + str(loop_cnt) + " Time: " + time.strftime("%H:%M:%S",
                                                                                          time.gmtime(elapsed_time)))

                self.state = STATE_MISSIONS
                if self.do_single_loop == True:  # we did one loop, return
                    ap.update_ap_status("Single Loop Complete")
                    return

                    # Useful Journal data that might be able to leverage
            # if didn't make it to Robigo Mines (at the ring), need to retry
            #"timestamp":"2022-05-08T23:49:43Z", "event":"SupercruiseExit", "Taxi":false, "Multicrew":false, "StarSystem":"Robigo", "SystemAddress":9463020987689, "Body":"Robigo 1 A Ring", "BodyID":12, "BodyType":"PlanetaryRing" }

            #This entry shows we made it to the Robigo Mines
            #{ "timestamp":"2022-05-08T23:51:43Z", "event":"SupercruiseExit", "Taxi":false, "Multicrew":false, "StarSystem":"Robigo", "SystemAddress":9463020987689, "Body":"Robigo Mines", "BodyID":64, "BodyType":"Station" }

            # if we get these then we got mission complete and made it to Sirius Atmos, if not we are short
            #  "event":"MissionRedirected", "NewDestinationStation":"Robigo Mines", "NewDestinationSystem":"Robigo", "OldDestinationStation":"", "OldDestinationSystem":"Sothis" }

            # if didn't make it to Sirius Atmos, go back into SC
            #{ "timestamp":"2022-05-08T22:01:27Z", "event":"SupercruiseExit", "Taxi":false, "Multicrew":false, "StarSystem":"Sothis", "SystemAddress":3137146456387, "Body":"Sothis A 5", "BodyID":14, "BodyType":"Planet" }

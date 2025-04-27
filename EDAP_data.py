"""
Static data.

For easy reference any variable should be prefixed with the name of the file it
was either in originally, or where the primary code utilising it is.

Note: Some of this file comes from EDMarketConnector's edmc_data.py file
(https://github.com/EDCD/EDMarketConnector/blob/main/edmc_data.py).

"""

# Status.json / Dashboard Flags constants
FlagsDocked = 1 << 0             # on a landing pad in space or planet
FlagsLanded = 1 << 1             # on planet surface (not planet landing pad)
FlagsLandingGearDown = 1 << 2
FlagsShieldsUp = 1 << 3
FlagsSupercruise = 1 << 4         # While in super-cruise
FlagsFlightAssistOff = 1 << 5
FlagsHardpointsDeployed = 1 << 6
FlagsInWing = 1 << 7
FlagsLightsOn = 1 << 8
FlagsCargoScoopDeployed = 1 << 9
FlagsSilentRunning = 1 << 10
FlagsScoopingFuel = 1 << 11
FlagsSrvHandbrake = 1 << 12
FlagsSrvTurret = 1 << 13         # using turret view
FlagsSrvUnderShip = 1 << 14      # turret retracted
FlagsSrvDriveAssist = 1 << 15
FlagsFsdMassLocked = 1 << 16
FlagsFsdCharging = 1 << 17       # While charging and jumping for super-cruise or system jump
FlagsFsdCooldown = 1 << 18       # Following super-cruise or jump
FlagsLowFuel = 1 << 19           # < 25%
FlagsOverHeating = 1 << 20       # > 100%, or is this 80% now ?
FlagsHasLatLong = 1 << 21        # On when altimeter is visible (either OC/DRP mode or 2Km/SURF mode).
FlagsIsInDanger = 1 << 22
FlagsBeingInterdicted = 1 << 23
FlagsInMainShip = 1 << 24
FlagsInFighter = 1 << 25
FlagsInSRV = 1 << 26
FlagsAnalysisMode = 1 << 27      # Hud in Analysis mode
FlagsNightVision = 1 << 28
FlagsAverageAltitude = 1 << 29   # Altitude from Average radius. On when altimeter shows OC/DRP, Off if altimeter is not shown or showing 2Km/SURF.
FlagsFsdJump = 1 << 30           # While jumping to super-cruise or system jump. See also Flags2FsdHyperdriveCharging.
FlagsSrvHighBeam = 1 << 31

# Status.json / Dashboard Flags2 constants
Flags2OnFoot = 1 << 0
Flags2InTaxi = 1 << 1  # (or dropship/shuttle)
Flags2InMulticrew = 1 << 2  # (ie in someone else’s ship)
Flags2OnFootInStation = 1 << 3
Flags2OnFootOnPlanet = 1 << 4
Flags2AimDownSight = 1 << 5
Flags2LowOxygen = 1 << 6
Flags2LowHealth = 1 << 7
Flags2Cold = 1 << 8
Flags2Hot = 1 << 9
Flags2VeryCold = 1 << 10
Flags2VeryHot = 1 << 11
Flags2GlideMode = 1 << 12
Flags2OnFootInHangar = 1 << 13
Flags2OnFootSocialSpace = 1 << 14
Flags2OnFootExterior = 1 << 15
Flags2BreathableAtmosphere = 1 << 16
Flags2TelepresenceMulticrew = 1 << 17
Flags2PhysicalMulticrew = 1 << 18
Flags2FsdHyperdriveCharging = 1 << 19       # While charging and jumping for system jump
Flags2FsdScoActive = 1 << 20
Flags2Future21 = 1 << 21
Flags2Future22 = 1 << 22
Flags2Future23 = 1 << 23
Flags2Future24 = 1 << 24
Flags2Future25 = 1 << 25
Flags2Future26 = 1 << 26
Flags2Future27 = 1 << 27
Flags2Future28 = 1 << 28
Flags2Future29 = 1 << 29
Flags2Future30 = 1 << 30
Flags2Future31 = 1 << 31

# Status.json Dashboard GuiFocus constants
GuiFocusNoFocus = 0              # ship view
GuiFocusInternalPanel = 1        # right hand side
GuiFocusExternalPanel = 2        # left hand (nav) panel
GuiFocusCommsPanel = 3		     # top
GuiFocusRolePanel = 4		     # bottom
GuiFocusStationServices = 5
GuiFocusGalaxyMap = 6
GuiFocusSystemMap = 7
GuiFocusOrrery = 8
GuiFocusFSS = 9
GuiFocusSAA = 10
GuiFocusCodex = 11

# Journal.log Ship Name constants
ship_name_map = {
    'adder':                        'Adder',
    'anaconda':                     'Anaconda',
    'asp':                          'Asp Explorer',
    'asp_scout':                    'Asp Scout',
    'belugaliner':                  'Beluga Liner',
    'cobramkiii':                   'Cobra Mk III',
    'cobramkiv':                    'Cobra Mk IV',
    'cobramkv':                     'Cobra Mk V',
    'corsair':                      'Corsair',
    'clipper':                      'Panther Clipper',
    'cutter':                       'Imperial Cutter',
    'diamondback':                  'Diamondback Scout',
    'diamondbackxl':                'Diamondback Explorer',
    'dolphin':                      'Dolphin',
    'eagle':                        'Eagle',
    'empire_courier':               'Imperial Courier',
    'empire_eagle':                 'Imperial Eagle',
    'empire_fighter':               'Imperial Fighter',
    'empire_trader':                'Imperial Clipper',
    'federation_corvette':          'Federal Corvette',
    'federation_dropship':          'Federal Dropship',
    'federation_dropship_mkii':     'Federal Assault Ship',
    'federation_gunship':           'Federal Gunship',
    'federation_fighter':           'F63 Condor',
    'ferdelance':                   'Fer-de-Lance',
    'hauler':                       'Hauler',
    'independant_trader':           'Keelback',
    'independent_fighter':          'Taipan Fighter',
    'krait_mkii':                   'Krait Mk II',
    'krait_light':                  'Krait Phantom',
    'mamba':                        'Mamba',
    'mandalay':                     'Mandalay',
    'orca':                         'Orca',
    'python':                       'Python',
    'python_nx':                    'Python Mk II',
    'scout':                        'Taipan Fighter',
    'sidewinder':                   'Sidewinder',
    'testbuggy':                    'Scarab',
    'type6':                        'Type-6 Transporter',
    'type7':                        'Type-7 Transporter',
    'type8':                        'Type-8 Transporter',
    'type9':                        'Type-9 Heavy',
    'type9_military':               'Type-10 Defender',
    'typex':                        'Alliance Chieftain',
    'typex_2':                      'Alliance Crusader',
    'typex_3':                      'Alliance Challenger',
    'viper':                        'Viper Mk III',
    'viper_mkiv':                   'Viper Mk IV',
    'vulture':                      'Vulture',
}

# Journal.log Ship Name to size constants
ship_size_map = {
    'adder':                         'S',
    'anaconda':                      'L',
    'asp':                           'M',
    'asp_scout':                     'M',
    'belugaliner':                   'L',
    'cobramkiii':                    'S',
    'cobramkiv':                     'S',
    'cobramkv':                      'S',
    'corsair':                       'M',
    'clipper':                       '',
    'cutter':                        'L',
    'diamondback':                   'S',
    'diamondbackxl':                 'S',
    'dolphin':                       'S',
    'eagle':                         'S',
    'empire_courier':                'S',
    'empire_eagle':                  'S',
    'empire_fighter':                '',
    'empire_trader':                 'L',
    'federation_corvette':           'L',
    'federation_dropship':           'M',
    'federation_dropship_mkii':      'M',
    'federation_gunship':            'M',
    'federation_fighter':            '',
    'ferdelance':                    'M',
    'hauler':                        'S',
    'independant_trader':            'M',
    'independent_fighter':           '',
    'krait_mkii':                    'M',
    'krait_light':                   'M',
    'mamba':                         'M',
    'mandalay':                      'M',
    'orca':                          'L',
    'python':                        'M',
    'python_nx':                     'M',
    'scout':                         '',
    'sidewinder':                    'S',
    'testbuggy':                     '',
    'type6':                         'M',
    'type7':                         'L',
    'type8':                         'L',
    'type9':                         'L',
    'type9_military':                'L',
    'typex':                         'M',
    'typex_2':                       'M',
    'typex_3':                       'M',
    'viper':                         'S',
    'viper_mkiv':                    'S',
    'vulture':                       'S',
}

# Journal.log Ship Name to size constants
fuelscoop_rate_map = {
    'int_fuelscoop_size1_class1': 18.00,    # Size 1 Class E
    'int_fuelscoop_size1_class2': 24.00,    # Size 1 Class D
    'int_fuelscoop_size1_class3': 30.00,    # Size 1 Class C
    'int_fuelscoop_size1_class4': 36.00,    # Size 1 Class B
    'int_fuelscoop_size1_class5': 42.00,    # Size 1 Class A

    'int_fuelscoop_size2_class1': 32.00,    # Size 2 Class E
    'int_fuelscoop_size2_class2': 43.00,    # Size 2 Class D
    'int_fuelscoop_size2_class3': 54.00,    # Size 2 Class C
    'int_fuelscoop_size2_class4': 65.00,    # Size 2 Class B
    'int_fuelscoop_size2_class5': 75.00,    # Size 2 Class A

    'int_fuelscoop_size3_class1': 75.00,    # Size 3 Class E
    'int_fuelscoop_size3_class2': 100.00,   # Size 3 Class D
    'int_fuelscoop_size3_class3': 126.00,   # Size 3 Class C
    'int_fuelscoop_size3_class4': 151.00,   # Size 3 Class B
    'int_fuelscoop_size3_class5': 176.00,   # Size 3 Class A

    'int_fuelscoop_size4_class1': 147.00,   # Size 4 Class E
    'int_fuelscoop_size4_class2': 196.00,   # Size 4 Class D
    'int_fuelscoop_size4_class3': 245.00,   # Size 4 Class C
    'int_fuelscoop_size4_class4': 294.00,   # Size 4 Class B
    'int_fuelscoop_size4_class5': 343.00,   # Size 4 Class A

    'int_fuelscoop_size5_class1': 247.00,   # Size 5 Class E
    'int_fuelscoop_size5_class2': 330.00,   # Size 5 Class D
    'int_fuelscoop_size5_class3': 412.00,   # Size 5 Class C
    'int_fuelscoop_size5_class4': 494.00,   # Size 5 Class B
    'int_fuelscoop_size5_class5': 577.00,   # Size 5 Class A

    'int_fuelscoop_size6_class1': 376.00,   # Size 6 Class E
    'int_fuelscoop_size6_class2': 502.00,   # Size 6 Class D
    'int_fuelscoop_size6_class3': 627.00,   # Size 6 Class C
    'int_fuelscoop_size6_class4': 752.00,   # Size 6 Class B
    'int_fuelscoop_size6_class5': 878.00,   # Size 6 Class A

    'int_fuelscoop_size7_class1': 534.00,   # Size 7 Class E
    'int_fuelscoop_size7_class2': 712.00,   # Size 7 Class D
    'int_fuelscoop_size7_class3': 890.00,   # Size 7 Class C
    'int_fuelscoop_size7_class4': 1068.00,  # Size 7 Class B
    'int_fuelscoop_size7_class5': 1245.00,  # Size 7 Class A

    'int_fuelscoop_size8_class1': 720.00,   # Size 8 Class E
    'int_fuelscoop_size8_class2': 960.00,   # Size 8 Class D
    'int_fuelscoop_size8_class3': 1200.00,  # Size 8 Class C
    'int_fuelscoop_size8_class4': 1440.00,  # Size 8 Class B
    'int_fuelscoop_size8_class5': 1680.00,  # Size 8 Class A
}

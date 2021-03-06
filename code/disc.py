#!/usr/bin/env python
#----------------------------------------------------------------------
# helper routines 
#---------------------------------------------------------------------.
asciiart = """
180 150W  120W  90W   60W   30W  000   30E   60E   90E   120E  150E 180
|    |     |     |     |     |    |     |     |     |     |     |     |
+90N-+-----+-----+-----+-----+----+-----+-----+-----+-----+-----+-----+
|          . _..::__:  ,-"-"._       |7       ,     _,.__             |
|  _.___ _ _<_>`!(._`.`-.    /        _._     `_ ,_/  '  '-._.---.-.__|
|.{     " " `-==,',._\{  \  / {)     / _ ">_,-' `                mt-2_|
+ \_.:--.       `._ )`^-. "'      , [_/( G        e      o     __,/-' +
|'"'     \         "    _L       0o_,--'                )     /. (|   |
|         | A  n     y,'          >_.\\._<> 6              _,' /  '   |
|         `. c   s   /          [~/_'` `"(   l     o      <'}  )      |
+30N       \\  a .-.t)          /   `-'"..' `:._        c  _)  '      +
|   `        \  (  `(          /         `:\  > \  ,-^.  /' '         |
|             `._,   ""        |           \`'   \|   ?_)  {\         |
|                `=.---.       `._._ i     ,'     "`  |' ,- '.        |
+000               |a    `-._       |     /          `:`<_|h--._      +
|                  (      l >       .     | ,          `=.__.`-'\     |
|                   `.     /        |     |{|              ,-.,\     .|
|                    |   ,'          \ z / `'            ," a   \     |
+30S                 |  /             |_'                |  __ t/     +
|                    |o|                                 '-'  `-'  i\.|
|                    |/                                        "  n / |
|                    \.          _                              _     |
+60S                            / \   _ __  _   _  ___ __ _ ___| |_   +
|                     ,/       / _ \ | '_ \| | | |/ __/ _` / __| __|  |
|    ,-----"-..?----_/ )      / ___ \| | | | |_| | (_| (_| \__ \ |_ _ |
|.._(                  `----'/_/   \_\_| |_|\__, |\___\__,_|___/\__| -|
+90S-+-----+-----+-----+-----+-----+-----+--___/ /--+-----+-----+-----+
     Based on 1998 Map by Matthew Thomas   |____/ Hacked on 2015 by 8^/  

"""

import math,collections
# Index of refraction for optical fiber
FIBER_RI = 1.52
SPEED_OF_LIGHT = 299792.458 # km/s

class Disc(object):
    def __init__(self, hostname, latitude, longitude, ping,ttl):
        """
        ping (float): (in ms)
        """ 
        self._radius    = ping*0.001 * SPEED_OF_LIGHT / FIBER_RI / 2  # in km:ping*98,615940132
        self._hostname  = hostname
        #self._instance  = instance
        #self._city=city
        #self._valid=valid
        #self._oldradius=oldradius
        self._latitude=latitude
        self._longitude=longitude
        self._ttl=ttl

    def getHostname(self):
        return self._hostname

    def getLatitude(self):
        return self._latitude

    def getTime(self):
        return self._time
    def setTime(self,time):
        self._time=time

    def getLongitude(self):
        return self._longitude

    def getRadius(self):
        return self._radius

    def getTtl(self):
        return self._ttl

    def overlap(self, other):
        """
        Two discs overlap if the distance between their centers is lower than
        the sum of their radius.
        """
        
        return (self.distanceFromTheCenter(other._latitude,other._longitude)) <= (self.getRadius() + other.getRadius())

    def distanceFromTheCenter(self,lat, longi):
        # Convert latitude and longitude to 
        # spherical coordinates in radians.
        degrees_to_radians = math.pi/180.0
            
        # phi = 90 - latitude
        phi1 = (90.0 - self._latitude)*degrees_to_radians
        phi2 = (90.0 - lat)*degrees_to_radians
            
        # theta = longitude
        theta1 = self._longitude*degrees_to_radians
        theta2 = longi*degrees_to_radians
            
        # Compute spherical distance from spherical coordinates.
            
        # For two locations in spherical coordinates 
        # (1, theta, phi) and (1, theta, phi)
        # cosine( arc length ) = 
        #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
        # distance = rho * arc length
        
        cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
               math.cos(phi1)*math.cos(phi2))
        if (abs(cos - 1.0) <0.000000000000001):
            arc=0.0   
        else:
            arc = math.acos( cos )
            
        # Remember to multiply arc by the radius of the earth 
        # in your favorite set of units to get length.
        return arc*6371


    def __str__(self):
        return "%s\t%s\t%s\t%s\n" % (self._hostname, self._latitude,  self._longitude, self._radius)

class Discs(object):

    def __init__(self):
        self._setDisc={}
        self._orderDisc=collections.OrderedDict()

    def getDiscs(self):
        return self._setDisc

    def removeDisc(self, disc):
        self._setDisc[disc[0].getRadius()].remove(disc)

    def overlap(self, other):

        for radius, listDisc in self._setDisc.iteritems():
            
            for disc in listDisc:
                if disc[0].overlap(other):
                    return True
        return False
    

    def add(self,disc,geolocated):
        if(self._setDisc.get(disc.getRadius()) is None):
           self._setDisc[disc.getRadius()]=[(disc,geolocated)]
        else:
            self._setDisc[disc.getRadius()].append((disc,geolocated))

    def getOrderedDisc(self):
        self._orderDisc=collections.OrderedDict(sorted(self._setDisc.items()))
        return self._orderDisc

    def smallestDisc(self):
        self._orderDisc=collections.OrderedDict(sorted(self._setDisc.items()))
        return next(iter(self._orderDisc))


#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# helper functions to launch RIPE Atlas measurement  (./igreedy -m target -p -r)
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

import json
import time
import os
import string
import sys
import time
import getopt
import socket
import collections
import webbrowser
import random

import RIPEAtlas
import subprocess



class Ripe(object):
    def __init__(self, ip,ripeProbes=None,timestamp=None):

        if(checkIP(ip)):
            self._ip = ip
        else:
            print >>sys.stderr, ("Target must be an IP address, NOT AN HOST NAME")
            sys.exit(1)

        self._timestamp=timestamp
        self._ripeProbes = ripeProbes
        self._numberOfPacket =2 #to improve
        self._numberOfProbes = 5 #to improve, introduce as parameter, in alternative to the list of probes
        self._measurement = None
        self.result = None
        self._defaultPath="./datasets/ripe-vps"
        self._percentageSuccessful = 0.8 
        self._numberVPsInFile=sum(1 for line in open(self._defaultPath))-1 #header

    def setTimestamp(self,timestamp):
        self._timestamp=timestamp

    def getIP(self):
        return self._ip

    def getRipeProbes(self):
        return self._ripeProbes

    def loadProbes(self,VPs=None):
        temp_list_probes=[]
        temp_information_probes={}
        countNumberLine=-1 #flag for random VPs selection
        if VPs is None:
            pathVPs = self._defaultPath
        elif VPs.isdigit():
            numberVPS=int(VPs)
            if(numberVPS>self._numberVPsInFile):
                print "ERROR: number of VPs required bigger than the number of VPs in ./datasets/ripe-vps"
                sys.exit()
            pathVPs=self._defaultPath
            randomLines=random.sample(range(1, self._numberVPsInFile),numberVPS)
            countNumberLine=0
        else:
            pathVPs=VPs

        tempInformationProbes={}
        tempListProbes=[]
        
        for line in open(pathVPs,'r').readlines():
            if line.startswith("#"): #skip header and comments
                continue 
            if countNumberLine>=0:
                countNumberLine+=1
                if countNumberLine not in randomLines:
                    continue
            hostname,latitude,longitude,country = line.strip().split("\t")
            temp_list_probes.append(hostname)
            temp_information_probes[hostname]=[latitude,longitude,country]
        self._numberOfProbes=len(temp_list_probes)
        return (",".join(temp_list_probes),temp_information_probes) #building the list

    def doMeasure(self,listProbes):
    
        data = { "definitions": [
               { "target": self._ip, "description": "Ping %s" % self._ip,
               "type": "ping", "is_oneoff": True, "packets": self._numberOfPacket} ],
             "probes": [
                 { "requested": self._numberOfProbes} ] }
        data["probes"][0]["type"] = "probes"
        data["probes"][0]["value"] = listProbes

        if string.find( self._ip, ':') > -1:
            af = 6
        else:
            af = 4
        data["definitions"][0]['af'] = af
        print "Running measurement from Ripe Atlas:"
        self.measurement = RIPEAtlas.Measurement(data)
        print "ID measure: %s\tTARGET: %s\tNumber of Vantage Points: %i " % (self.measurement.id,  self._ip,self.measurement.num_probes)

    def retrieveResult(self,infoProbes):
        self.result = self.measurement.results(wait=True, percentage_required=self._percentageSuccessful)
        print self.result
        numVpAnswer=0
        numVpFail=0
        totalRtt = 0
        numLatencyMeasurement = 0
        numVpTimeout = 0
        print("Number of answers: %s" % len(self.result))
        if(self._timestamp is None):
            self._timestamp=str(time.time()).split(".")[0]
        pathFile="datasets/measurement/"+self._ip+"-"+self._timestamp
        inputIgreedyFiles=open(pathFile,'a')
        inputIgreedyFiles.write("#hostname	latitude	longitude	rtt[ms]	ttl	country\n")
        inputIgreedyFiles.write("#ripeID measurement:\t"+str(self.measurement.id)+"\n")

        for result in self.result:

            VP = result["prb_id"]
            try:
                ttl=result["ttl"]
            except:
                print result
                ttl=-1
            for measure in result["result"]:
                numVpAnswer += 1
                if measure.has_key("rtt"):
                    totalRtt += int(measure["rtt"])
                    numLatencyMeasurement += 1
                    inputIgreedyFiles.write(str(VP)+"\t"+str(infoProbes[str(VP)][0])+"\t"+str(infoProbes[str(VP)][1])+"\t"+str(measure["rtt"])+"\t"+str(ttl)+"\t"+infoProbes[str(VP)][2]+"\n")
                elif measure.has_key("error"):
                    numVpFail += 1
                elif measure.has_key("x"):
                    numVpTimeout += 1
                else:
                    print >>sys.stderr, ("Error in the measurement: result has no field rtt, or x or error")
        inputIgreedyFiles.close()
        if numVpAnswer == 0:
            print("Watson, we have a problem, no successful test!")
            sys.exit(0)
        else:
            try:
                print("Resume: %i successful tests (%.1f %%), %i errors (%.1f %%), %i timeouts (%.1f %%), average RTT: %i ms" % \
                      (numLatencyMeasurement,numLatencyMeasurement*100.0/numVpAnswer, 
                       numVpFail, numVpFail*100.0/numVpAnswer, 
                       numVpTimeout, numVpTimeout*100.0/numVpAnswer, totalRtt/numLatencyMeasurement))
            except:
                  c=0
        return (numLatencyMeasurement,pathFile)


class PlanetLab(object):
    def __init__(self, ip,numberOfPacket,planetlabProbes=None,timestamp=None):
        if(checkIP(ip)):
            self._ip = ip
        else:
            print >>sys.stderr, ("Target must be an IP address, NOT AN HOST NAME")
            sys.exit(1)

        self.pathVPs = "datasets/planetlab-vps-all"
        self.pingResultsTemp="/tmp/tempPing"
        self._numberOfPacket = numberOfPacket 
        self._timestamp=timestamp

        self._planetlabProbes = "datasets/planetlab-vps"
        self._numberVPsInFile=sum(1 for line in open(self._planetlabProbes))-1 #header

        if planetlabProbes.isdigit():
            numberVPS=int(planetlabProbes)
            if(numberVPS>self._numberVPsInFile):
                print "ERROR: number of VPs required bigger than the number of VPs in ./datasets/planetlab-vps"
                sys.exit()
            randomLines=random.sample(range(1, self._numberVPsInFile),numberVPS)
            countNumberLine=0 
            tempPlanetlabProbes="/tmp/planetlab-vps-selected"
            tempFile=open(tempPlanetlabProbes,'w')
            for line in open(self.pathVPs,'r').readlines(): #generating the random VPs
                if line.startswith("#"): #skip header and comments
                    tempFile.write(line)
                    continue 
                countNumberLine+=1
                if countNumberLine not in randomLines:
                    continue
                tempFile.write(line)
            tempFile.close()
            self._planetlabProbes=tempPlanetlabProbes
        else:
            self._planetlabProbes = planetlabProbes

    def setTimestamp(self,timestamp):
        self._timestamp=timestamp

    def getIP(self):
        return self._ip

    def getProbes(self):
        return self._planetlabProbes

    def checkAliveNodes(self,pathVPs=None):
        
        subprocess.call("./code/ping-pl.sh 1",shell=True) #run experiment
        return None

    def doMeasure(self):
        print "Running measurement from PlanetLab"
        print "./code/ping-pl.sh 0 "+self._ip+" "+self.pingResultsTemp+" "+str(self._numberOfPacket)+" 0 "+self._planetlabProbes
        subprocess.call("bash code/ping-pl.sh 0 "+self._ip+" "+self.pingResultsTemp+" "+str(self._numberOfPacket)+" 0 "+self._planetlabProbes,shell=True) #run experiment

    def retrieveResult(self):
        filePingResults=open(self.pingResultsTemp+"/"+self._ip)


        #load planetlab information -------------------put in another function
        planetLabInfo={}
        listPlanetlabProbes=open(self.pathVPs)
        for line in listPlanetlabProbes.readlines():
                if line.startswith("#"):
                    continue
                hostname,latitude,longitude,city,country=line.strip().split("\t")[0:5]
                planetLabInfo[hostname]=[hostname,latitude,longitude,country]
        #END load planetlab information -------------------put in another function

        if(self._timestamp is None):
            self._timestamp=str(time.time()).split(".")[0]
        pathFile="datasets/measurement/"+self._ip+"-"+self._timestamp

        if(not os.path.isfile(pathFile)):
            inputIgreedyFiles=open(pathFile,'a')
            inputIgreedyFiles.write("#hostname	latitude	longitude	rtt[ms]	ttl	country\n")
        else:
            inputIgreedyFiles=open(pathFile,'a')
        numLatencyMeasurement=0

        for line in filePingResults.readlines():

           if line.startswith("#"):
              continue
           try:
               hostname,ttl,ping=line.strip().split(" ")
               info=planetLabInfo[hostname]
               try:
                    if isinstance(float(ping), float) and isinstance(int(ttl), int) :
                        #inputIgreedyFiles.write("\t".join(planetLabInfo[hostname])+"\t"+ping+"\t"+ttl+"\n") #igreedy 1.2
                        inputIgreedyFiles.write(hostname+"\t"+info[1]+"\t"+info[2]+"\t"+ping+"\t"+ttl+"\t"+info[3]+"\n")
                        numLatencyMeasurement += 1
               except:
                        pass #nothing to do
           except:
               pass #nothing to do
        return (numLatencyMeasurement,pathFile)

def checkIP(str):
    try:
        addr = socket.inet_pton(socket.AF_INET6, str)
    except socket.error: # not a valid IPv6 address
        try:
            addr = socket.inet_pton(socket.AF_INET, str)
        except socket.error: # not a valid IPv4 address either
            return False
    return True


#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# main user program to process  (./igreedy for help)
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


from selenium import webdriver
import sys, getopt, math,  time
import os.path
import shutil
#./igreedy.py inputFile outputFile json <----json output
#inputFile: separated by \t:hostname\tlatitude\tlongitude\tping
#outputFile:

from anycast import Anycast,Object
from measurement import Ripe,PlanetLab
from disc import *
import webbrowser
from threading import Thread
import argparse
from output import Output
from Stream_controller import Stream_controller
authfile = "datasets/auth"


#iatafile = '../datasets/airports.csv'
iatafile = './datasets/airports.csv'
infile = ''
outfile = 'output'
outformat = "csv"
gtfile = ''
alpha = 1  #advised settings
browser  = False 
noise = 0  #exponential additive noise, only for sensitivity analysis

IATA = []
IATAlat = {}
IATAlon = {}
IATAcity = {}
PAI = []
GT = {}
PAInum = 0
GTnum = 0

numberOfInstance = 0
truePositive = 0
falsePositive = 0 
loadtime = 0
runtime = 0
threshold = -1 # negative means infty


def airportDistance(a,b):
        if (a not in IATAlat) or  (b not in IATAlat):  
            return "NaN"  
        lat1 = IATAlat[a] 
        lat2 = IATAlat[b]
        lon1 = IATAlon[a] 
        lon2 = IATAlon[b] 

        # Convert latitude and longitude to 
        # spherical coordinates in radians.
        degrees_to_radians = math.pi/180.0
            
        # phi = 90 - latitude
        phi1 = (90.0 - lat1)*degrees_to_radians
        phi2 = (90.0 - lat2)*degrees_to_radians
            
        # theta = longitude
        theta1 = lon1*degrees_to_radians
        theta2 = lon2*degrees_to_radians
            
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


def readIATA():
    """
    Routine to read IATA
    """
    #IATA size name lat long countryCode city pop heuristic h1 h2 h3
    global iatafile, IATA, IATAlat, IATAlon, IATAcity
    temp = []
    data = open(iatafile)
    data.readline() #consume header
    for line in data.readlines():
        stuff = line.strip().split("\t")
        iata = stuff[0].upper()
        temp.append(iata)
        latlon = stuff[3]
        (lat,lon) = latlon.split(" ")
        IATAlat[iata] = float(lat)
        IATAlon[iata] = float(lon)
        IATAcity[iata] = stuff[5]
    IATA = set(temp)
    IATAcity["NoCity"] = "NoCity"



def readGT():
    """
    Routine to read groundtruth(GT)( / public available information (PAI)
    """
    global gtfile, GT, PAI, IATA, IATAlat, IATAlon, IATAcity, GTnum, PAInum,GTtotal

    GTlist = []
    PAIlist = []
    temp=[]
    if gtfile is None:
        return
    if not os.path.isfile(gtfile):
        return

    data = open(gtfile)
    for line in data.readlines():
        if line.startswith("#"):
            continue
        iata = ""
        fields = line.strip().split("\t")
        if(len(fields)==2):  
            #ground truth measured from a specific vantage point
            hostname  = fields[0]
            iata = fields[1].upper()
            GT[hostname] = iata
            if (iata not in IATA and hostname != "#hostname"):
                print "Weird ground truth: <" + iata + "> for <" + hostname + ">"
                #raw_input( "Weird ground truth: <" + iata + "> for <" + hostname + ">\n"
                #"This ground truth will be not considered in the validation\nPress Enter to continue...")

                #actually the measuremtn should not be counted as we have information we do not know how to handle
                #yet the following trick avoid runtime errors (key not found)
                IATAlat[iata]=0
                IATAlon[iata]=0
                IATAcity[iata]="Weird"
            else:
                GTlist.append( iata )

        elif(len(fields)==1):
            #publicly avlable information, but not tied to a specific host
            iata=fields[0].upper() 
            temp.append( iata )
            if (iata not in IATA):
                print "Weird publicly available information: <" + iata + ">"
                #"This ground truth will be not considered in the validation\nPress Enter to continue...")
                #actually the measuremtn should not be counted as we have information we do not know how to handle
                #yet the following trick avoid runtime errors (key not found)
                IATAlat[iata]=0
                IATAlon[iata]=0
                IATAcity[iata]="Weird"
            else:
                PAIlist.append( iata ) 

        else:
            print "Unexpected ground truth format: ", line

    PAI = set(PAIlist)   
    PAInum = len(set(PAIlist))
    GTtotal=set(GTlist)
    GTnum = len(set(GTlist))
    

def analyze():
    """
    Routine to iteratively enumerate and geolocate anycast instances
    """
    global infile, outfile, gtfile, iatafile
    global alpha, browser, noise, threshold
    global numberOfInstance, discsSolution
    global anycast

    anycast=Anycast(infile,iatafile,alpha,noise,threshold)

    radiusGeolocated=0.1
    treshold=0 #tolerance, airport out of the disc
    iteration=True
    discsSolution=[]

    numberOfInstance=0
    while(iteration is True):
        iteration=False
        resultEnumeration=anycast.enumeration()
  
        numberOfInstance+=resultEnumeration[0]
        if(numberOfInstance<=1):
            print "No anycast instance detected"
            #sys.exit()
        for radius, discList in resultEnumeration[1].getOrderedDisc().iteritems(): 
            for disc in discList:
                if(not disc[1]): #if the disc was not geolocated before, geolocate it!
                    #used for the csv output
                    #discs.append(disc[0])#append the disc to the results #used for the csv output
                    resultEnumeration[1].removeDisc(disc) #remove old disc from MIS of disc  
                    city=anycast.geolocation(disc[0],treshold) #result geolocation

                    if(city is not False): #if there is a city inside the disc
                        iteration=True #geolocated one disc, re-run enumeration!
                        #markers.append(newDisc)#save for the results the city#used for the csv output 
                        discsSolution.append((disc[0],city)) #disc, marker
                        resultEnumeration[1].add(Disc("Geolocated",float(city[1]),float(city[2]),radiusGeolocated,-1),True) #insert the new disc in the MIS
                        break #exit for rerun MIS
                    else:
                        resultEnumeration[1].add(disc[0],True) #insert the old disc in the MIS
                        discsSolution.append((disc[0],["NoCity",disc[0].getLatitude(),disc[0].getLongitude(),"N/A","N/A"])) #disc, marker
                        
            if(iteration):
                break


#-*--------------other classes!!!!!
def output(num):
    """
    Routine to output results to a JSON (for GoogleMaps) and a CSV (for further processing)
    """
    global infile, outfile, outformat, alpha, gtfile, base, loadtime, runtime
    global listSolutionTtl,listSolutionRtt #used for the cdf in the browser
    global numberOfInstance, discSolution, truePositive, falsePositive, GT, PAI, IATAlat, IATAlon, IATAcity, GTnum, PAInum, weirdGtSolution
    weirdGtSolution=0

    # Results as a CSV    
    csv=open(outfile + ".csv","w")
    csv.write("#hostname\tcircleLatitude\tcircleLongitude\t" +\
              "radius\tttl\tiataCode\tiataLatitude\tiataLongitude\t"+\
              "city\tcode_country\n")
    listSolutionTtl=[]
    listSolutionRtt=[]
    for instance in discsSolution:  #circle to csv
        csv.write(instance[0].getHostname()+"\t"+\
                    str(instance[0].getLatitude())+"\t"+\
                    str(instance[0].getLongitude())+"\t"+\
                    str(instance[0].getRadius())+"\t"+\
                    str(instance[0].getTtl())+"\t"+\
                    str(instance[1][0])+"\t"+\
                    str(instance[1][1])+"\t"+\
                    str(instance[1][2])+"\t"+\
                    str(instance[1][3])+"\t"+\
                    str(instance[1][4])+"\n")
        listSolutionRtt.append(instance[0].getRadius())
        listSolutionTtl.append(instance[0].getTtl())
    csv.close()

        # Results as a CSV
    csv=open("./outputs/"+outfile+str(num)+ ".csv","w")
    csv.write("#hostname\tcircleLatitude\tcircleLongitude\t" +\
              "radius\tttl\tiataCode\tiataLatitude\tiataLongitude\t"+\
              "city\tcode_country\n")
    listSolutionTtl=[]
    listSolutionRtt=[]
    for instance in discsSolution:  #circle to csv
        csv.write(instance[0].getHostname()+"\t"+\
                    str(instance[0].getLatitude())+"\t"+\
                    str(instance[0].getLongitude())+"\t"+\
                    str(instance[0].getRadius())+"\t"+\
                    str(instance[0].getTtl())+"\t"+\
                    str(instance[1][0])+"\t"+\
                    str(instance[1][1])+"\t"+\
                    str(instance[1][2])+"\t"+\
                    str(instance[1][3])+"\t"+\
                    str(instance[1][4])+"\n")
        listSolutionRtt.append(instance[0].getRadius())
        listSolutionTtl.append(instance[0].getTtl())
    csv.close()


    print "Number latency measurements: ",  sum(1 for line in open(infile)) -1
    print "Elapsed time (load+igreedy): %.2f (%.2f + %.2f)" % (loadtime+runtime, loadtime, runtime)
    print "Instances: ", str(numberOfInstance)
    # Comparing to the Ground-truth
    if gtfile is not None:
        print "Validation with ground truth or public available information:"
        errors = []
        Mlist = [] #list with the iata code present in the solution
        meanErr = 0
        pseudoVar = 0
        meanOld = 0
        #fragile
    
        for instance in discsSolution:  #circle to csv
            #comparing vs. GT or PAI
            iata = instance[1][0]
            gt=""
            Mlist.append( iata )   #measured airport instance

            if GTnum>0: #if there is at least one GT
                gt = GT[instance[0].getHostname()]
                if(IATAcity[gt] is "Weird"):
                    weirdGtSolution+=1
                    continue
            if (gt == iata ):
                print "TP [GT] "+ gt +"("+ IATAcity[gt] +")"
                truePositive += 1
            elif (iata in PAI):
                print "TP [PAI] ",  iata 
                truePositive += 1
            else:
                if GTnum>0 : #if there is a gt
                    distance = airportDistance(gt, iata)
                elif PAInum>0: #if we are here should always go in one branch
                    distance=20000 #antipodes distance
                    if iata is not "NoCity":
                        for airportPAI in PAI:
                            newDistance=airportDistance(iata,airportPAI)
                            if(newDistance<distance):
                               distance=newDistance
                               gt=airportPAI
                    else:
                         print "Circle without city inside:validation not possible" #CHECK WITH DARIO
                         continue

                if IATAcity[gt] == IATAcity[iata]:
                    print "TP [SameCity] " + gt +"("+ IATAcity[gt] +") "+ iata +"("+ IATAcity[iata] +") "
                    truePositive += 1

                elif(distance < 99): 
                    # Neighboring airports as e..g, EWR and JFK for NewYork, despite they are 
                    # not in the same City, they however serve the same population. 
                    # The distance EWR,JFK is 33Km
                    # Same thing for ORY, CDG and BVA for Paris: while PAR aggregates ORY and CDG, 
                    # it does not include Beauvais (BVA). The distance BVA,ORY is 83Km.
                    # Hence we select a threshold of 99Km (98.615940132), that corresponds to the distance the 
                    # light travels in 1ms considering a fiber medium.
                    print "TP [CloseCity] "+ gt +"("+ IATAcity[gt] +") "+ iata +"("+ IATAcity[iata] +") "
                    truePositive += 1

                else:    
                    print "FP [!!!] "+ gt +"("+ IATAcity[gt] +") "+ iata +"("+ IATAcity[iata] +") " 
                    falsePositive += 1
                    try:
                        meanErr += float((distance-meanOld)/float(falsePositive))
                        pseudoVar += float((distance-meanOld)*(distance-meanErr))
                        meanOld = meanErr
                        errors.append( distance )
                    except:
                        pass    
                        #cannot do much; distance is not a number likely because the selected City is not the provided IATA list                        
                        
        if falsePositive>1:                
            stdErr = math.pow(pseudoVar / (falsePositive-1), 0.5)
        else:
            stdErr = 0

        if weirdGtSolution>0:
            print "VPs with weird GT present in the solution:  %s" % (weirdGtSolution)

    # Results as a JSON

    data=Object()
    data.count= numberOfInstance
    data.instances=[]
    data.countGT=GTnum
    data.markerGT=[]
    data.countAllCircles=len(anycast.getDisc())
    data.allCircles=[]
    for instance in discsSolution:
            #circle to Json
            tempCircle=instance[0]  
            circle=Object()
            circle.id= tempCircle.getHostname()
            circle.latitude= tempCircle.getLatitude()
            circle.longitude= tempCircle.getLongitude()
            circle.radius= tempCircle.getRadius()
            circle.timestamp=tempCircle.getTime()

            #marker to Json
            tempMarker=instance[1]
            marker=Object()
            marker.id= tempMarker[0]
            marker.latitude= tempMarker[1]
            marker.longitude= tempMarker[2]
            marker.city=tempMarker[3]
            marker.code_country=tempMarker[4]
            markCircle=Object()
            markCircle.marker=marker
            markCircle.circle=circle
            data.instances.append(markCircle)
    #empty circle:
    for key,instance in anycast.getDisc().iteritems():
            #circle to Json
            tempCircle=instance[0]
            circle=Object()
            circle.id= tempCircle.getHostname()
            circle.latitude= tempCircle.getLatitude()
            circle.longitude= tempCircle.getLongitude()
            circle.radius= tempCircle.getRadius()
            circle.timestamp=tempCircle.getTime()
            data.allCircles.append(circle)        
    if GTnum>0:
        for gt in GTtotal:
            markerGT=Object()
            markerGT.id= gt
            markerGT.latitude= IATAlat[gt] 
            markerGT.longitude= IATAlon[gt]
            data.markerGT.append(markerGT)

    json=open(outfile + ".json","w")
    json.write("var data=\n")
    json.write(data.to_JSON())
    json.close()
    json=open("./outputs/"+outfile+str(num)+ ".json","w")
    json.write("var data=\n")
    json.write(data.to_JSON())
    json.close()
#####################################################################################  JOAN
    
    data2=Object()
    data2.variable=data
    json=open(outfile +"2"+ ".json","w")
    json.write("var data=\n")
    json.write(data2.to_JSON())
    json.close()
    
    
def threaded_browser():
    #url = "http://localhost:63342/igreedy-master/webDemo/demo.html"
    url ="./code/webDemo/demo.html"
    """
    refreshrate=8
    refreshrate=int(refreshrate)
    driver = webdriver.Firefox()
    #driver.get("http://"+url)
    driver.get(url)
    while True:
        time.sleep(refreshrate)
        driver.refresh()
    """

    webbrowser.open(url,new=2,autoraise=True)#open in a new tab, if possible
    


def help():
     print asciiart + """
usage:
    igreedy.py (-i INPUT | -m MEASUREMENT | -h) [-p (false)] [-r (false)] [-o OUTPUT] [-g GROUNDTRUTH] [-a ALPHA (1)] [-n NOISE (0)] [-t TRESHOLD (\infty)] [-b (false)]

where:
     -i input file
     -m IPV4 or IPV6 (real time measurements using the RIPE Atlas and/or PlanetLab vantage points in datasets/*-vps)  
     -o output prefix (.csv,.json)
     -g measured ground truth (GT) or publicly available information (PAI) files 
        (format: "hostname iata" lines for GT, "iata" lines for PAI)
     -a alpha (tune population vs distance score; was 0.5 in INFOCOM'15, now defaults to 1, more details in TECHREP-16 or INFOCOM'15)
     -b browser (visualize a GoogleMap of the results in a browser)
     -n noise (average of exponentially distributed additive latency noise; only for sensitivity)
     -t threshold (discard disks having latency larger than threshold to bound the error; discouraged)
     -r vantage points file or number of random vantage points (datasets/ripe-vps) for real time measurements from Ripe Atlas 
     -p vantage points file or number of random vantage points (datasets/planetlab-vps)real time measurements from PlanetLab 
     """ 
     sys.exit()

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
       raise argparse.ArgumentTypeError("The file %s does not exist!"%arg)
    else:
       return os.path.abspath(arg)  #return an open file handle

def restricted_float(x):
    x = float(x)
    if x < 0.0 or x > 1.0:
        raise argparse.ArgumentTypeError("Alpha must be [0.0,1.0], wrong choice: %r"%(x,))
    return x

def main(argv):
   global infile,  gtfile, outfile, threshold
   global alpha, browser, noise
   global loadtime, runtime
   starttime = time.time()
   ip=""
   ipPL=""
   
   parser = argparse.ArgumentParser(add_help=False)

   group = parser.add_mutually_exclusive_group(required=True)
   group.add_argument("-i", "--input",type=lambda x: is_valid_file(parser,x))
   group.add_argument("-m", "--measurement") #TODO: check if is valid IP
   group.add_argument("-h", "--help",action="store_true")

#m should be parents or they have to share the same parameter
   parser.add_argument("-p", "--planetlab",type=str)
   parser.add_argument("-r", "--ripe",type=str)
   
   parser.add_argument("-o", "--output",type=str,default='output')
   parser.add_argument("-g", "--groundtruth", type=lambda x: is_valid_file(parser,x))
   parser.add_argument("-a", "--alpha", type=restricted_float, default=1)
   parser.add_argument("-n", "--noise", type=float, default=0)
   parser.add_argument("-t", "--treshold", type=float )
   parser.add_argument("-b", "--browser", action="store_true")
 
   values = parser.parse_args()

   if values.help:
        help()

   infile=values.input
   ip=values.measurement
   outfile=values.output
   gtfile=values.groundtruth
   alpha=values.alpha
   noise=values.noise
   treshold=values.treshold
   planetLabList=values.planetlab
   ripeList=values.ripe
   browser=values.browser
   if infile is not None and ip is not None>0:
       help();
   elif infile is None and ip is None and ipPL is None:
        help();
   elif ip is not None and not(ripeList or planetLabList):
        help()

   key = open(authfile)
   auth = key.readline()[:-1]
   key.close()

   if ip:
      if(values.ripe):

          timestamp=str(time.time()).split(".")[0]
          measureRipe=Stream_controller(ripeList,ip,auth)
          #measureRipe.setTimestamp(timestamp)
          measureRipe.get_ID_list()
          measureRipe.doMeasurements()
          #listProbes,infoProbes=measureRipe.loadProbes(ripeList)
          """
          if(numLatencyMeasurement<2):
              print >>sys.stderr, ("Error: for the anycast detection at least 2 latency measurement are needed")
              sys.exit(-1)
          """
          #time.sleep(3)
          infile=measureRipe.get_infile()


          #a canviar


          print 'Airports:', iatafile
          readIATA()
          print 'Measurement:', infile
          print 'Ground-truth:', gtfile
          readGT()
          print 'Output:', outfile + ".{csv,json}"

          thread = Thread(target = threaded_browser)
          thread.start()

          actuallines=0
          output_number=0

          while True:
              tmplines=measureRipe.getlines()

              if tmplines>actuallines:
                  print "New output loop:\n"

                  loadtime = time.time() - starttime
                  starttime = time.time()
                  analyze()
                  runtime = time.time() - starttime


                  output(output_number)
                  if browser:


                      graphs=Output()
                      shutil.copy2(outfile+".json", "code/webDemo/data/anycastJson/output.json") #copy file in the directory for the browser
                      shutil.copy2("./outputs/"+outfile+str(output_number)+".json", "code/webDemo/data/anycastJson/outputs/output"+str(output_number)+".json")
                      graphs.generateRttCDFs("cdfRtt.json",listSolutionRtt,anycast.getAllRtt())
                      graphs.generateTtlCDFs("cdfTtl.json",listSolutionTtl,anycast.getAllTtl())
                      graphs.generatePlatfromPie("platformPie.json",anycast.getNumberPlanetLabVp(),anycast.getNumberRipeVp())
                      graphs.generateCountryPie("countryPie.json",anycast.getCountryStatistic())

                      shutil.move("cdfRtt.json", "code/webDemo/data/graphs/CDF/cdfRtt.json")
                      shutil.move("cdfTtl.json", "code/webDemo/data/graphs/CDF/cdfTtl.json")
                      shutil.move("platformPie.json", "code/webDemo/data/graphs/PIE/platformPie.json")
                      shutil.move("countryPie.json", "code/webDemo/data/graphs/PIE/countryPie.json")

                      """
                      #url = "./code/webDemo/demo.html"
                      #url="./code/webDemo/demo.html"

                      webbrowser.open(url,new=0,autoraise=True)#open in a new tab, if possible
                      """

                      # open a public URL, in this case, the webbrowser docs


                      """
                      driver = webdriver.Firefox()
                      print "3"
                      #driver.get("http://"+url)
                      driver.get(url)
                      print "4"
                      driver.refresh()
                      print "5"
                      """
                      actuallines=tmplines

                      data=Object()
                      data.count=output_number

                      json=open("./outputs/number.json","w")
                      json.write("var counts=\n")
                      json.write(data.to_JSON())
                      json.close()
                      shutil.copy2("./outputs/number.json", "code/webDemo/data/anycastJson/outputs/number.json")
                      output_number+=1

              time.sleep(1)


      else:
          #TODO:launch 2 threads
          timestamp=str(time.time()).split(".")[0]
          """
          if(values.ripe):
              measureRipe=Ripe(ip)
              measureRipe.setTimestamp(timestamp)
              listProbes,infoProbes=measureRipe.loadProbes(ripeList)
              measureRipe.doMeasure(listProbes)
              numLatencyMeasurement,infile=measureRipe.retrieveResult(infoProbes)
              if(numLatencyMeasurement<2):
                  print >>sys.stderr, ("Error: for the anycast detection at least 2 latency measurement are needed")
                  sys.exit(-1)
          """
          if(values.planetlab):
              measurePlanetlab=PlanetLab(ip,5,planetLabList)
              measurePlanetlab.setTimestamp(timestamp)
              measurePlanetlab.doMeasure() #---------add here the probes as parameters
              numLatencyMeasurement,infile=measurePlanetlab.retrieveResult()
              if(numLatencyMeasurement<2):
                  print >>sys.stderr, ("Error: for the anycast detection at least 2 latency measurement are needed")
                  sys.exit(-1)


          print 'Airports:', iatafile
          readIATA()
          print 'Measurement:', infile
          print 'Ground-truth:', gtfile
          readGT()
          print 'Output:', outfile + ".{csv,json}"

          loadtime = time.time() - starttime
          starttime = time.time()
          analyze()
          runtime = time.time() - starttime

          output()
          print "ciao"
          if browser:
           print "ciao"
           graphs=Output()
           shutil.copy2(outfile+".json", "code/webDemo/data/anycastJson/output.json") #copy file in the directory for the browser
           graphs.generateRttCDFs("cdfRtt.json",listSolutionRtt,anycast.getAllRtt())
           graphs.generateTtlCDFs("cdfTtl.json",listSolutionTtl,anycast.getAllTtl())
           graphs.generatePlatfromPie("platformPie.json",anycast.getNumberPlanetLabVp(),anycast.getNumberRipeVp())
           graphs.generateCountryPie("countryPie.json",anycast.getCountryStatistic())

           shutil.move("cdfRtt.json", "code/webDemo/data/graphs/CDF/cdfRtt.json")
           shutil.move("cdfTtl.json", "code/webDemo/data/graphs/CDF/cdfTtl.json")
           shutil.move("platformPie.json", "code/webDemo/data/graphs/PIE/platformPie.json")
           shutil.move("countryPie.json", "code/webDemo/data/graphs/PIE/countryPie.json")


           # open a public URL, in this case, the webbrowser docs
           thread = Thread(target = threaded_browser)
           thread.start()






if __name__ == "__main__":
   main(sys.argv[1:])

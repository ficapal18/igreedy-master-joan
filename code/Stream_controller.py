
from ripe.atlas.cousteau import AtlasStream
import os, subprocess,time,json
from Stream import Threadstream
import Handler
from subprocess import PIPE,Popen
from threading import Thread
import time
from datetime import datetime
from ripe.atlas.cousteau import (
  Ping,
  AtlasSource,
  AtlasCreateRequest
)
import sys




global infoProbes,listProbes,ID_list
ripeList="./datasets/ripe-vps"
result="./code/theresult"
falsa="Ghost_VP_ID"
ID_list=[]
finalFile="final_report"
listProbes=[]
infoProbes=[]


class Stream_controller():

    def __init__(self,ripeList,ip,auth):
        self.ripeList=ripeList
        self.target=ip
        self.auth=auth


    def setTimestamp(self,timestamp):
        self.timestamp=timestamp

    def get_ID_list(self):

       print "Checking IP List"

       ripe_list=Handler.loadprobes(self.ripeList)


       self.msm_id=self.create_measurement(self.target,ripe_list[0],self.auth)


       IO_file=open("./code/theresult",'w')
       IO_file.write(str(self.msm_id))

       print "1st step finished, IDs are available"


    def doMeasurements(self):

        IO_file=open("./datasets/measurement/"+self.msm_id,'a')
        IO_file.write("#hostname	latitude	longitude	rtt[ms]	ttl	country\n")
        #IO_file.write("#hostname	latitude	longitude	country\n")
        IO_file.write("#ripeID measurement:\t"+str(self.msm_id)+"\n")
        url="https://atlas.ripe.net/api/v1/measurement/"+self.msm_id+"/result/"
        print url
        IO_file.close()

        self.listProbes,self.infoProbes=Handler.loadprobes(self.ripeList)

        thread=Threadstream(self.infoProbes,self.msm_id)
        thread.start()
        self.infile=thread.get_info()

    def get_infile(self):
        print "\ninfile: ./datasets/measurement/"+self.msm_id
        return "./datasets/measurement/"+self.msm_id

    def getlines(self):
        with open("./datasets/measurement/"+self.msm_id) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def create_measurement(self,target,probe_ids,auth):
        """
        ATLAS_API_KEY = "107e6fb0-be49-4d0d-a4bd-c1d25ca85dd5"


        ping = Ping(af=4,target=target, description="ping",probe_id= 3183)#probe_ids

        source = AtlasSource(type="area", value="WW", requested=5)

        atlas_request = AtlasCreateRequest(
            start_time=datetime.utcnow(),
            key=ATLAS_API_KEY,
            measurements=[ping],
            sources=[source],
            is_oneoff=True
        )

        (is_success, response) = atlas_request.create()

        print is_success
        print response["measurements"]
        return  response["measurements"]

        #curl --dump-header - -H "Content-Type: application/json" -H "Accept: application/json" -X POST -d '{"definitions": [{"target": "mashable.com","af": 4,"packets": 3,"size": 40,"description": "Ping measurement to mashable.com","interval": 240,"resolve_on_probe": false,"type": "ping"}],"probes": [{"value": "1,2,3,4,5,6","type": "probes","requested": 6}],"is_oneoff": false}' https://atlas.ripe.net/api/v1/measurement/?key='107e6fb0-be49-4d0d-a4bd-c1d25ca85dd5'
        """
        #print "hello %s" % (name,)
        print target
        print probe_ids
        number=len(probe_ids.split(","))

        #cmd="--dump-header - -H \"Content-Type: application/json\" -H \"Accept: application/json\" -X POST -d \'{\"definitions\": [{\"target\": \"%s\",\"af\": 4,\"packets\": 3,\"size\": 40,\"description\": \"Ping measurement\",\"interval\": 240,\"resolve_on_probe\": false,\"type\": \"ping\"}],\"probes\": [{\"value\": \"%s\",\"type\": \"probes\",\"requested\": 6}],\"is_oneoff\": false}\' https://atlas.ripe.net/api/v1/measurement/?key=\'107e6fb0-be49-4d0d-a4bd-c1d25ca85dd5\'"%(target,probe_ids)

        a="curl"
        b="--dump-header"
        c="-"
        d="-H"
        e="\"Content-Type: application/json\""
        f="-H"
        g="\"Accept: application/json\""
        h="-X"
        i="POST"
        j="-d"
        jj="b8332b99-400a-4eeb-ae07-5b124c6f2178"
        jj=auth
        k="\'{\"definitions\": [{\"target\": \"%s\",\"af\": 4,\"packets\": 3,\"size\": 48,\"description\": \"Ping measurement \",\"resolve_on_probe\": false,\"type\": \"ping\"}],\"probes\": [{\"value\": \"%s\",\"type\": \"probes\",\"requested\": %s}],\"is_oneoff\": true}\' https://atlas.ripe.net/api/v1/measurement/?key=\'%s\' "%(target,probe_ids,number,jj)
        cmd=(" ").join([a,b,c,d,e,f,g,h,i,j,k])
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        out, err = p.communicate()
        print out,err
        out=out.split('\n')

        out=out[-1]

        out=out[17:24]
        print "Measurement id:",out

        if out[1:3]==":4":
            print "--------------------------------------------------------------------------------------------------------------------------------------------------------------"
            sys.exit()
        return out














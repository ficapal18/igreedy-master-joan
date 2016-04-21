from threading import Thread
from ripe.atlas.cousteau import AtlasStream
import Handler
import time
from anycast import Object
import shutil


class Threadstream(Thread):

    def __init__(self, infoprobes,id):
        Thread.__init__(self)
        self.id=id
        self.infoprobes=infoprobes
        #self.ts=ts
        self.infile="./datasets/measurement/"+str(id)
        #self.timestamp_file="../timestamp"



    def run(self):
        atlas_stream = AtlasStream()
        atlas_stream.connect()
        # Measurement results
        channel = "result"
        # Bind function we want to run with every result message received
        atlas_stream.bind_channel(channel, self.on_result_response)
        # Subscribe to new stream for 1001 measurement results
        #stream_parameters = {"msm": ID_list,"startTime": ts}
        #ID_list.append(1001)
        #print self.id

        #ID_list = map(int, self.id)
        #ID_list=(1001)

        #ID_list.append('1001')

        stream_parameters = {"msm":self.id} #,"startTime": self.ts
        atlas_stream.start_stream(stream_type="result",**stream_parameters)

        # Probe's connection status results
        channel = "probe"
        atlas_stream.bind_channel(channel, self.on_result_response)
        #stream_parameters = {"prb": (12605,13663,850),"startTime": ts,"enrichProbes": True}
        #,"start_time":1456948500
        stream_parameters = {} #,"startTime": self.ts
        atlas_stream.start_stream(stream_type="probestatus", **stream_parameters)

        # Timeout all subscriptions after 5 secs. Leave seconds empty for no timeout.
        # Make sure you have this line after you start *all* your streams
        atlas_stream.timeout(seconds=1200)
        # Shut down everything
        atlas_stream.disconnect()

    def on_result_response(self,*args):
        """
        Function that will be called every time we receive a new result.
        Args is a tuple, so you should use args[0] to access the real message.
        """
        #############################################################print args[0]

        #self.changeTimestamp(time.time())
        self.infile=Handler.retrieveResult(self.infoprobes,args[0])
        #result_data = json.dumps(args[0])
        #result_data=ast.literal_eval(args[0])
        #result_data = json.load(args[0])

        data=[]
        """
        data=Object()

        data.timestamp=time.time()

        json=open(self.timestamp_file + ".json","w")
        json.write("var timestamps=\n")
        json.write(data.to_JSON())
        json.close()
        shutil.copy2(self.timestamp_file+".json", "./code/webDemo/data/anycastJson/timestamp.json") #copy file in the directory for the browser
        """

    def get_info(self):
        return self.infile

    def changeTimestamp(self,data):

        #datas=Object()
        json=open(self.timestamp_file + ".json","w")
        json.write("var timestamp=\n")
        json.write(int(data).to_JSON())
        json.close()








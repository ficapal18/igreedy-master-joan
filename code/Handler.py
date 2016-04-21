import time
from anycast import Object
import shutil
from threading import Lock
ripeList="./datasets/ripe-vps"
result="./code/theresult"
ID_list=[]
finalFile="./code/final_report"
listProbes=[]
infoProbes=[]
mutex=Lock()
tmp_first_latency=0
timestamp_file="./timestamp"

def loadprobes(ripeList):
    temp_list_probes=[]
    temp_information_probes={}

    pathVPs=ripeList

    for line in open(pathVPs,'r').readlines():
        if line.startswith("#"): #skip header and comments
            continue

        hostname,latitude,longitude,country = line.strip().split("\t")
        temp_list_probes.append(hostname)
        temp_information_probes[hostname]=[latitude,longitude,country]
    return (",".join(temp_list_probes),temp_information_probes) #building the list


def retrieveResult(infoProbes,result_data):
        """
            datasets = Updater.Directory('/datasets')
            datasets.refresh()

            datasets.helper.join()
            for d in [datasets] + datasets.dirs:
                for f in d.files:
                  print f
        """

        if "result" in result_data:
            print "\n--------------------------------->     USEFUL PACKET RECEIVED\n"

            numVpAnswer=0
            numVpFail=0
            totalRtt = 0
            numLatencyresultment = 0
            numVpTimeout = 0
            #print result_data
            #result=ast.literal_eval(result_data)
            print("Number of answers: %s" % len(result_data))
            print("\nRetrieving Result\n")

            result=result_data
            VP = result["prb_id"]
            #print VP
            try:
                ttl=result["ttl"]
            except:
                #print result
                ttl=-1
            #print result
            for i,measure in enumerate(result["result"]):

                IO_file=open("./datasets/measurement/"+str(result["msm_id"]), 'a')
                numVpAnswer += 1


                if result["result"][0].has_key("rtt"):

                    numLatencyresultment += 1
                    a=infoProbes[infoProbes.keys()[0]]
                    #print result["result"][0]["rtt"]
                    #el bo
                    #IO_file.write(str(VP)+"\t"+str(infoProbes[str(VP)][0])+"\t"+str(infoProbes[str(VP)][1])+"\t"+str(result["result"][0]["rtt"])+"\t"+str(ttl)+"\t"+infoProbes[str(VP)][2]+"\n")

                    IO_file.write(str(VP)+"\t"+str(infoProbes[str(VP)][0])+"\t"+str(infoProbes[str(VP)][1])+"\t"+str(result["result"][i]["rtt"])+"\t"+str(ttl)+"\t"+infoProbes[str(VP)][2]+"\n")


                    #IO_file.write(str(VP)+"\t"+str(a[0])+"\t"+str(a[1])+"\t"+str(result["result"][0]["rtt"])+"\t"+str(ttl)+"\t"+a[2]+"\n")

                elif result["result"][0].has_key("error"):
                    numVpFail += 1
                elif result["result"][0].has_key("x"):
                    numVpTimeout += 1
                else:
                    print ("Error in the resultment: result has no field rtt, or x or error")
                IO_file.close()
                #mutex.release()


                data=Object()

                data.timestamp=time.time()

                json=open(timestamp_file + ".json","w")
                json.write("var timestamps=\n")
                json.write(data.to_JSON())
                json.close()
                shutil.copy2(timestamp_file+".json", "./code/webDemo/data/anycastJson/timestamp.json") #copy file in the directory for the browser
            return (tmp_first_latency+numLatencyresultment,"./code/datasets/measurement"+str(result["msm_id"]))
        else:
            print "PACKET WITHOUT INFORMATION"